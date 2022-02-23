from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import time
from uuid import uuid4
import json

import sensors
from motor import motor


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

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
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    payload = json.loads(payload)
    print(payload['close_window'])
    if payload['close_window'] == 1:
          motor(1,-1)

    print("Received message from topic '{}': {}".format(topic, payload))


if __name__ == '__main__':
    try:
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)


        endpoint = 'a31gd9kluhs5xl-ats.iot.us-east-2.amazonaws.com'
        cert_path = 'certs/certificate.pem.crt'
        pk_path = 'certs/private.pem.key'
        ca_path = 'certs/Amazon-root-CA-1.pem'
        client_id = f"RaspberryPi-{str(uuid4())}"
        receiver_topic = 'remote'
        sender_topic = 'rpi'

        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            port=8883,
            cert_filepath=cert_path,
            pri_key_filepath=pk_path,
            client_bootstrap=client_bootstrap,
            ca_filepath=ca_path,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=client_id,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=None)

        print(f"Connecting to {endpoint} with client ID '{client_id}'...")

        connect_future = mqtt_connection.connect()

        # Future.result() waits until a result is available
        connect_future.result()
        print("Connected!")

        # Subscribe
        print("Subscribing to topic '{}'...".format(receiver_topic))
        
        subscribe_future, packet_id = mqtt_connection.subscribe(
            topic=receiver_topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_message_received)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))

        sensors.setup()

        while True:
            message = f"temp&humid={sensors.getTempHumid()}, isRaining={sensors.isRaining()}"
            print("Publishing message to topic '{}': {}".format(sender_topic, message))
            message_json = json.dumps(message)
            mqtt_connection.publish(
                topic=sender_topic,
                payload=message_json,
                qos=mqtt.QoS.AT_LEAST_ONCE)
            time.sleep(5)


    except KeyboardInterrupt:
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")

