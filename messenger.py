import json
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
from uuid import uuid4


class messenger:
    def __init__(self) -> None:
        self.lock = False
        self.event_loop_group = io.EventLoopGroup(1)
        self.host_resolver = io.DefaultHostResolver(self.event_loop_group)
        self.client_bootstrap = io.ClientBootstrap(
            self.event_loop_group, self.host_resolver)

        self.endpoint = 'a31gd9kluhs5xl-ats.iot.us-east-2.amazonaws.com'
        self.cert_path = 'certs/certificate.pem.crt'
        self.pk_path = 'certs/private.pem.key'
        self.ca_path = 'certs/Amazon-root-CA-1.pem'
        self.client_id = f"RaspberryPi-{str(uuid4())}"

        # Callback when connection is accidentally lost.
        def on_connection_interrupted(connection, error, **kwargs):
            print("Connection interrupted. error: {}".format(error))

        # Callback when an interrupted connection is re-established.
        def on_connection_resumed(connection, return_code, session_present, **kwargs):
            print("Connection resumed. return_code: {} session_present: {}".format(
                return_code, session_present))
            if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
                print("Session did not persist. Resubscribing to existing topics...")
                resubscribe_future, _ = connection.resubscribe_existing_topics()

                # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
                # evaluate result with a callback instead.
                resubscribe_future.add_done_callback(on_resubscribe_complete)

        def on_resubscribe_complete(resubscribe_future):
            resubscribe_results = resubscribe_future.result()
            print("Resubscribe results: {}".format(resubscribe_results))

            for topic, qos in resubscribe_results['topics']:
                if qos is None:
                    sys.exit(
                        "Server rejected resubscribe to topic: {}".format(topic))

        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=self.endpoint,
            port=8883,
            cert_filepath=self.cert_path,
            pri_key_filepath=self.pk_path,
            client_bootstrap=self.client_bootstrap,
            ca_filepath=self.ca_path,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=self.client_id,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=None
        )

        print(
            f"Connecting to {self.endpoint} with client ID '{self.client_id}'...")

    def connect(self):
        conn_future = self.mqtt_connection.connect()
        conn_res = conn_future.result()
        print(conn_res)
        return conn_res

    def send(self, topic: str, payload: dict, preempt: bool=False) -> str:
        if (self.lock and not preempt):
            return
        resp = json.dumps(payload)

        self.mqtt_connection.publish(
            topic=topic,
            payload=resp,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )

        print(f"sent msg to topic {topic}, content {resp}")

    def subscribe(self, topic: str, callback):
        # def on_msg_received(payload, dup, qos, retain, **kwargs):
        def on_msg_received(payload, **kwargs):
            payload = json.loads(payload)
            print(f"received msg {payload}")
            callback(payload)

        print(f"Subscribing to topic '{topic}'...")

        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_msg_received)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))

    def disconnect(self):
        print("Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
