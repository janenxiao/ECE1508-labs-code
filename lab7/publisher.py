"""
Created on Mar, 2021
@author: Morteza Moghaddassian
@Project: ECE1508 - NetSoft Course
"""
# paho is a client library to communicate with Mosquitto broker that implements MQTT V3.1.1 (MMG)
import paho.mqtt.client as paho
import psutil
import time
import inspect

'''
    @class_name: Publisher
    @role: Publishing contents to the message broker.
    @number of methods: 3
    @access modifier: public    
'''


class Publisher:
    # The broker address.
    broker_address = None
    # The port that the broker is listening on for incoming connections. The default is 1883 for Mosquitto broker.
    broker_port = None

    '''
        @input: address, port
        @role: Constructor method
    '''
    def __init__(self, address, port):
        # The broker IP address (142.150.208.235)
        self.broker_address = address
        # The broker port number (1883)
        self.broker_port = int(port)

    def on_publish(self, client, userdata, result):
        pass

    '''
        @input: topic, message (The content that has to be published).
        @role: Publishing the message to the broker.
        @info: This method maintains a request-respond model with the caller.
    '''
    def publish(self, topic, message):
        # Creating a paho (MQTT) client object.
        pub = paho.Client()
        pub.on_publish = self.on_publish
        # Connecting the "pub" object to the message broker.
        pub.connect(self.broker_address,self.broker_port)
        # Publishing the data.
        answer = pub.publish(topic, message)
        print("Published "+topic+" number "+message)
        # Disconnecting the client paho (MQTT) objecct.
        pub.disconnect()


if __name__ == "__main__":       
    # to be completeled by students...
    broker_address = "142.150.208.235"
    broker_port = 1883
    publisher = Publisher(broker_address, broker_port)

    interval_seconds = 60   # sleep for 60 seconds after each publish
    while True:
        # CPU Utilization
        cpu_percent = psutil.cpu_percent(interval=interval_seconds)
        publisher.publish("ece1508/netsoft7/cpu_percent", str(cpu_percent))
        # print("cpu_percent: {}".format(cpu_percent))

        # Memory Utilization
        virtual_memory = psutil.virtual_memory()
        mem_total = virtual_memory.total /1024/1024    # in MB
        publisher.publish("ece1508/netsoft7/mem_total", str(mem_total))

        mem_used = virtual_memory.used /1024/1024    # in MB
        publisher.publish("ece1508/netsoft7/mem_used", str(mem_used))

        mem_free = virtual_memory.free /1024/1024    # in MB
        publisher.publish("ece1508/netsoft7/mem_free", str(mem_free))

        mem_percent = virtual_memory.percent       # percentage of utilization
        publisher.publish("ece1508/netsoft7/mem_percent", str(mem_percent))

        # Network I/O statistics
        netio_eth0 = psutil.net_io_counters(pernic=True)["eth0"]
        bytes_sent = netio_eth0.bytes_sent       # in bytes
        publisher.publish("ece1508/netsoft7/bytes_sent", str(bytes_sent))

        bytes_recv = netio_eth0.bytes_recv       # in bytes
        publisher.publish("ece1508/netsoft7/bytes_recv", str(bytes_recv))

        time.sleep(interval_seconds)
    
    # print( inspect.getsource(paho.Client.publish) )
    # print( inspect.getmembers(paho.Client) )



