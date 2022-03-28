#!/bin/bash
network_status=`curl -o /dev/null -s -w "%{http_code}\n" www.google.com`;
expected=200;
while [ $network_status != $expected ]
do
    echo "retry network test";
    network_status=`curl -o /dev/null -s -w "%{http_code}\n" www.google.com`;
done

echo "network connected!";

. venv/bin/activate
python main.py
