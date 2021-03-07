#!/usr/bin/env python3
"""
Usage::
    ./server.py <path to options.json>
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from paho.mqtt import client as mqtt_client

import logging
import jwt
import json
import random
import time

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'


class S(BaseHTTPRequestHandler):
    def _set_response(self, rc=200):
        self.send_response(rc)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("LDE usage only".encode('utf-8'))

    def do_POST(self):
        global mqtt_topic

        sud_data_map = {
            "T": "Temperature",
            "P": "pH",
            "N": "Ammonia"
        }

        # <--- Gets the size of data
        content_length = int(self.headers['Content-Length'])
        # <--- Gets the data itself
        post_data = self.rfile.read(content_length)

        response_code = 200
        response = "OK\n"

        if 'X-SENEYE' in self.headers:
            seneye_id = self.headers['X-SENEYE']
            secret = get_secret(seneye_id)
            if secret:
                try:
                    lde_response = jwt.decode(post_data.decode(
                        'utf-8'), secret, algorithms=['HS256'])
                    if lde_response['SUD']['data']['S']['S'] == 1:
                        logging.warning(
                            'Seneye slide has expired. pH and ammonia readings will not be available.')

                    if lde_response['SUD']['data']['S']['W'] == 1:
                        for key in sud_data_map:
                            if key in lde_response['SUD']['data']:
                                logging.info(
                                    sud_data_map[key] + ": " + str(lde_response['SUD']['data'][key]))
                                publish(
                                    mqtt_topic + '/' + seneye_id.lower() + '/' + sud_data_map[key].lower(), lde_response['SUD']['data'][key])

                        logging.info(
                            "Published available values to mqtt server.")
                    else:
                        logging.error(
                            'Seneye SUD is reporting it is not in water. Not using received readings.')
                except:
                    response = "Failed to decode payload.\n"
                    response_code = 400
                    logging.error("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                                  str(self.path), str(self.headers), post_data.decode('utf-8'))
                    logging.error(
                        "Unexpected data was received. Please verify your SWS secret is set correctly.")
            else:
                logging.error(
                    self.headers['X-SENEYE'] + " is not defined in secrets configuration.")
                response_code = 401
                response = "Unauthorized.\n"
        else:
            logging.error("X-SENEYE header missing from POST request.")
            response_code = 400
            response = "Bad request.\n"

        self._set_response(response_code)
        self.wfile.write(response.encode('utf-8'))


def get_secret(key):
    global seneye
    secret = None

    if len(key.split('_')) == 2:
        seneye_type = key.split('_')[0]
        seneye_serial = key.split('_')[1]

        for device in seneye:
            if device['type'] == seneye_type and device['serial'] == seneye_serial:
                secret = device['secret']

    return secret


def publish(topic, msg):
    result = client.publish(topic, msg, qos=1, retain=True)
    status = result[0]
    if status != 0:
        logging.error('Could not send message to mqtt server')


def connect_mqtt():
    global mqtt_server, mqtt_port, mqtt_username, mqtt_password

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT server")
        else:
            logging.error("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(mqtt_username, mqtt_password)
    client.on_connect = on_connect
    client.connect(mqtt_server, mqtt_port)
    return client


def run(server_class=HTTPServer, handler_class=S, port=8080):
    global client
    logging.basicConfig(format='%(levelname)-14s %(asctime)-24s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting mqtt client...')
    client = connect_mqtt()
    client.loop_start()
    logging.info('Starting httpd...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        config_file = str(argv[1])
        try:
            with open(config_file) as f:
                config_data = json.load(f)
            mqtt_server = config_data['mqtt_server']
            mqtt_port = config_data['mqtt_port']
            mqtt_username = config_data['mqtt_username']
            mqtt_password = config_data['mqtt_password']
            mqtt_topic = config_data['mqtt_topic']
            seneye = config_data['seneye']
            run()
        except:
            logging.error('Could not open/parse config file.')
    else:
        logging.error('Path to options.json must be specified.')
