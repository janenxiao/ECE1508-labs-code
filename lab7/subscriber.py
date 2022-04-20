"""
Created on Mar, 2021
@author: Morteza Moghaddassian
@Project: ECE1508 - NetSoft Course
"""
# paho is a client library to communicate with Mosquitto broker that implements MQTT V3.1.1
import paho.mqtt.client as paho
import time
from datetime import datetime
from multiprocessing import Process, Manager
import os
import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mpl_dates
import pandas

'''
    @class_name: Subscriber
    @role: Subscribing for contents and keeping them in memory.
    @number of methods: 4
    @access modifier: public    
'''


class Subscriber:
    # The topic that the subscriber needs to use for receiving the content from the message broker.
    subscriber_topic = None
    # Broker IP address.
    broker_address = None
    # The port that the broker is listening on for incoming connections. The default is 1883 for Mosquitto broker.
    broker_port = None    
    # Is used to save the message received from the broker.
    message_received = ''    

    '''
        @input: address, port, topic
        @role: Constructor method
    '''
    def __init__(self, address, port, topic, shared_dict):
        # The broker IP address (142.150.208.235)
        self.broker_address = str(address)
        # The broker port number (1883)
        self.broker_port = int(port)
        # Subscription Topic
        self.subscriber_topic = str(topic)
        
        # Shared dict to record data received from broker
        self.shared_dict = shared_dict 
       

    '''
        @input: client, userdate, flags, rc
        @role: Is being used to pair with the on_connect method on the broker to exchange the subscription topic.
    '''
    def on_connect(self, client, userdata, flags, rc):
        # Subscribing for contents with the specified topic.
        client.subscribe(self.subscriber_topic)

    '''
        @input: client, userdata, message
        @role: Is being used to pair with the on_message method on the broker to exchange the message with the topic of interest.
    '''
    def on_message(self, client, userdata, message):
	    # Printing the message which is obtained from the broker.
        msg_str = str(message.payload, encoding='utf-8')
        print(msg_str)

        # Update the topic data in shared_dict
        info = self.subscriber_topic[self.subscriber_topic.rfind('/')+1:]
        self.shared_dict[info] = (msg_str, datetime.now())
        # print(self.shared_dict)

        # Disconnecting from the broker.
        client.disconnect()

    '''
        @role: Subscribing to the broker and enabling the retrieval of the contents specified by the topics of interest.
    '''
    def subscribe(self):
        # Creating an MQTT client object.
        sub = paho.Client()
        # An infinite loop to keep the subscriber alive.
        while True:
            # Connecting to the broker.
            sub.connect(self.broker_address, self.broker_port)
            # Receiving the message (MMG)
            sub.on_message = self.on_message
            # Providing the topic of interest.
            sub.on_connect = self.on_connect
            # Keep the subscriber running until the whole message is received.
            sub.loop_forever()

'''
    @role: Process that runs a Subscriber object with a specific topic
'''
def do_subscribe(topic, shared_dict):
    print("do_subscribe process id = ", os.getpid())
    # signal.signal(signal.SIGINT, signal.SIG_IGN)    # ignore Interrupt from keyboard (CTRL + C), do not raise KeyboardInterrupt

    broker_address = "142.150.208.235"
    broker_port = 1883
    
    subscriber = Subscriber(broker_address, broker_port, topic, shared_dict)
    subscriber.subscribe()

'''
    @role: Process that periodically writes data in shared_dict to the timeseries file
'''
def do_writefile(tsfilename, info_topics, shared_dict, interval_sec):
    """will use info_topics[-1]'s timestamp in shared_dict to write row"""

    print("do_writefile process id = ", os.getpid())

    with open(tsfilename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        # Write header row
        csvwriter.writerow(info_topics + ["timestamp", "ts_writerow"])  # timestamp: time when lastinfo was received; ts_writerow: time when this row is written to file
    
    while True:
        time.sleep(interval_sec)

        lastinfo = info_topics[-1]
        lastinfo_ts = None
        data = []
        try:
            for info in info_topics:
                data.append(shared_dict[info][0])
                if info == lastinfo:
                    lastinfo_ts = shared_dict[info][1]
            
            data.append(lastinfo_ts)
            data.append(datetime.now())

            # Append a new row in the timeseries file
            with open(tsfilename, 'a', newline='') as csvfile:  # Windows newline characters:'\r\n', Unix:'\n', newline='' writes '\n' untranslated
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(data)
        
        except KeyError as keyerr:  # KeyError when the Subscriber has not received anything, thus has not created its entry in shared_dict
            print("Caught: \t", keyerr)

'''
    @role: The function that updates the matplotlib figure
'''
def animate(frame, *fargs):
    tsfilename, info_topics = fargs

    try:
        data = pandas.read_csv(tsfilename, parse_dates=["timestamp"])
        # print(plt.gcf().get_axes())
        # print(data)

        plt.clf()   # clear the current figure
        fig = plt.gcf()
        fig.set_constrained_layout(True)    # automatically adjust subplots and decorations like legends so that they fit in the figure
        # Divide the figure to a grid layout with 4 rows x 2 cols 
        gridspec = fig.add_gridspec(4, 2)  # add_gridspec(nrows, ncols) return a GridSpec: grid layout to place subplots within figure
        
        numinfo = len(info_topics)
        
        # Plot in each subplot
        for i in range(numinfo):
            info = info_topics[i]
            # add_subplot(nrows, ncols, index): add a subplot that will take the index position on a grid with nrows rows and ncols columns, index starts at 1 in the upper left corner
            # ax = fig.add_subplot(numinfo, 1, i+1)

            if i == 0:      # first subplot occupies the entire first row: gridspec[0, :]
                ax = fig.add_subplot(gridspec[i, :])
                # Format the dates in x majortick labels
                date_formatter = mpl_dates.DateFormatter('%H:%M')  # "%Y-%m-%d %H:%M:%S"
                ax.xaxis.set_major_formatter(date_formatter)        
                plt.xticks(horizontalalignment="right", rotation=10)    # set rotation of xtick labels
            else:
                ax = fig.add_subplot(gridspec[int((i+1)/2), (i+1)%2])
                # Do not show xtick labels for subplots except the first one to save space
                plt.setp(ax.get_xticklabels(), visible=False)   # set the xtick labels to be invisible
            
            # Plot the data in the subplot
            ax.plot_date(data["timestamp"], data[info])

            # Set relevant title for the subplot based on topic name
            if info.endswith("_percent"):
                title = info.replace("_percent", " utilization")
                title = title.replace("cpu", "CPU")
                title = title.replace("mem", "Memory")
                ax.set_title(title + " (%)")
                # ax.set_ylabel(title + " (%)")
            elif info.startswith("mem_"):
                title = info[4:]
                title = title.capitalize() + " memory"
                ax.set_title(title + " (MB)")
                # ax.set_ylabel(title + " (MB)")
            elif info.startswith("bytes_"):
                title = info.replace("_", " ")
                title = title.replace("recv", "received")
                title = title.capitalize() + " on eth0"
                ax.set_title(title)
                # ax.set_ylabel(title + " (byte)")

    except (pandas.errors.EmptyDataError, FileNotFoundError) as err:
        # pandas.errors.EmptyDataError when pandas.read_csv() reads an empty csv file, i.e. the file writing process has yet to write anything
        # FileNotFoundError when pandas.read_csv() cannot find the timeseries file, i.e. the file writing process has yet to create the file
        print("Caught: \t",err)

'''
    @role: Process that plots data in the timeseries file in real time
'''
def do_plotfile(tsfilename, info_topics, interval_sec):
    print("do_plotfile process id = ", os.getpid())

    # animate() is called every interval_sec seconds to update the figure
    ani = FuncAnimation(plt.gcf(), animate, interval=interval_sec*1000, fargs=(tsfilename, info_topics))
    plt.show()


if __name__ == "__main__":       
    # to be completeled by students...

    print("Parent process id = ", os.getpid())

    # Create a shared dict
    manager = Manager()
    shared_dict = manager.dict()
    
    # Write to file and plot from file every interval_sec seconds
    interval_sec = 60
    tsfilename = "timeseries.csv"
    
    info_topics = ["cpu_percent", "mem_total", "mem_used", "mem_free", "mem_percent", "bytes_sent", "bytes_recv"]
    processes = []

    # create do_subscribe() processes
    for info in info_topics:
        topic = "ece1508/netsoft7/" + info
        process = Process(target=do_subscribe, args=[topic, shared_dict])
        # process.daemon = True     # When a process exits, it attempts to terminate all of its daemonic child processes. Note that a daemonic process is not allowed to create child processes.
        process.start()
        processes.append(process)

    # create do_writefile() process
    process = Process(target=do_writefile, args=[tsfilename, info_topics, shared_dict, interval_sec])
    process.start()
    processes.append(process)

    # create do_plotfile() process
    process = Process(target=do_plotfile, args=[tsfilename, info_topics, interval_sec])
    process.start()
    processes.append(process)
    
    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        # when parent process receives CTRL-C, terminate all created processes
        print("Parent received CTRL-C")
        for process in processes:
            process.terminate()
            process.join()


    # do_subscribe("ece1508/netsoft7/cpu_percent", shared_dict)


