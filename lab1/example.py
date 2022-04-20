# Import mininet related packages
from mininet.net import Mininet
from mininet.node import Node, RemoteController, OVSController
from mininet.log import setLogLevel, info
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections, dumpNetConnections
from mininet.cli import CLI

def run():
  # Construct the network with cpu limited hosts and shaped links
  net = Mininet(host=CPULimitedHost, link=TCLink)
  
  # Create the network switches
  s1, s2, s3 = [net.addSwitch(s) for s in 's1', 's2', 's3']
  
  # Create network hosts, each having 10% of the system's CPU
  h1, h2, h3 = [net.addHost(h, cpu=0.1) for h in 'h1', 'h2', 'h3']
  
  # Tell mininet to use a remote controller located at 127.0.0.1:6653
  # c1 = RemoteController('c1', ip='127.0.0.1', port=6653)
  c1 = OVSController('c1')
  net.addController(c1)

  # Add link between switches. Each link has a delay of 5ms and 10Mbps bandwidth
  net.addLink(s1, s2, bw=10, delay='5ms')
  net.addLink(s2, s3, bw=10, delay='5ms')
  # net.addLink(s3, s1, bw=10, delay='5ms')

  # Add link between a host and a switch
  for (h, s) in [(h1, s1), (h2, s2), (h3, s3)]:
    net.addLink(h, s, bw=10, delay='10ms')
  
  # Start each switch and assign it to the controller
  for s in [s1, s2, s3]:
    s.start([c1])
  
  net.staticArp() # add all-pairs ARP entries to eliminate the need to handle broadcast
  net.start()

  # print "Dumping net connections"
  # dumpNetConnections(net)
  # print "Testing network connectivity"
  # net.pingAll()
  # CLI(net)  # open command-line interface
  # Start iperf server (-s) in h1
  h1.cmd('iperf -s &') 
  # Run a iperf client on h2 and print the throughput
  result = h2.cmd('iperf -yc -c ' + h1.IP() + ' -t 2').split(",")[-1] # test for 2 sec, parse the csv row to get the last item (bandwidth in bps)
  print "Throughput between h1<-->h2: " + str(float(result)/1000000.0) + "Mbps"
  CLI(net)
  net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
