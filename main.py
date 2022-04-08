import sys
import random
import time
import serial.tools.list_ports
from Adafruit_IO import MQTTClient

AIO_FEED_ID = ["dadn-brgt", "dadn-gas", "dadn-humi", "dadn-temp", "dadn-lcd-control", "dadn-prediction", "dadn-led"]
AIO_USERNAME = "khanh_trinh_ce"
AIO_KEY = "aio_ktyi40TIgxnB7nOufjXq3IxzaVBA"


def connected(client):
    print("Connected successfully.")
    for feed in range(4, 7):
        client.subscribe(AIO_FEED_ID[feed])


def subscribe(client, userdata, mid, granted_qos):
    print("Subscribed successfully.")


def disconnected(client):
    print("Disconnecting.")
    sys.exit(1)


def message(client, feed_id, payload):
    print("Received data: " + payload)


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_subscribe = subscribe
client.on_message = message
client.connect()
client.loop_background()
is_microbit_connected = False


def get_port():
    ports = serial.tools.list_ports.comports()
    n = len(ports)
    comm_port = "None"
    for i in range(n):
        port = ports[i]
        str_port = str(port)
        if "USB Serial Device" in str_port:
            split_port = str_port.split(" ")
            comm_port = split_port[0]
    return comm_port


if get_port() != "None":
    ser = serial.Serial(port= get_port(), baudrate=115200)
    is_microbit_connected = True


mess = ""


def process_data(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    split_data = data.split(":")
    print(split_data)
    try:
        if split_data[1] == "BRGT":
            client.publish("dadn-brgt", split_data[2])
        elif split_data[1] == "GAS":
            client.publish("dadn-gas", split_data[2])
        elif split_data[1] == "HUMI":
            client.publish("dadn-humi", split_data[2])
        elif split_data[1] == "TEMP":
            client.publish("dadn-temp", split_data[2])
        time.sleep(1)
    except:
        pass


def read_serial():
    bytes_to_read = ser.inWaiting()
    if bytes_to_read > 0:
        global mess
        mess = mess + ser.read(bytes_to_read).decode("UTF-8")
        while "#" in mess and "!" in mess:
            start = mess.find("!")
            end = mess.find("#")
            process_data(mess[start:end + 1])
            if end == len(mess):
                mess = ""
            else:
                mess = mess[end+1:]


while True:
    if is_microbit_connected:
        read_serial()
    for feed in range(4):
        client.publish(AIO_FEED_ID[feed], random.randint(0, 100))
        time.sleep(1)
    time.sleep(30)

