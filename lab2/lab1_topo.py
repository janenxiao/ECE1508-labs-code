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
  net = Mininet(host=CPULimitedHost, link=TCLink, autoStaticArp=True, autoSetMacs=True, cleanup=True)
  
  # Create the network switches
  sw = list() # sw[i] is 's(i+1), e.g. sw[0] is 's1'
  for i in range(6):
    s = net.addSwitch('s%s' % (i+1))
    sw.append(s)
  
  # Create network hosts, each having 10% of the system's CPU
  h1, h2, h3 = [net.addHost(h, cpu=0.1) for h in 'h1', 'h2', 'h3']

  # simple topology testing
  # s1 = net.addSwitch('s1')
  # net.addLink(h1, s1, port1=1, port2=3, bw=10, delay='15ms')
  # net.addLink(h2, s1, port1=1, port2=2, bw=10, delay='15ms')
  # net.addLink(h3, s1, port1=1, port2=1, bw=10, delay='15ms')
  
  # Tell mininet to use a remote controller located at 127.0.0.1:6653
  c1 = RemoteController('c1', ip='127.0.0.1', port=6653)
  # c1 = OVSController('c1')

  net.addController(c1)

  # Add link between switches
  for i in range(2):  # s1-s2, i.e. sw[0]-sw[1]
    for j in range(2, 6): # s3-s6
      si_num = int(sw[i].name[1])
      sj_num = int(sw[j].name[1])
      # link with a delay of 5ms and 15Mbps bandwidth; s1-eth3 connects to s3, s3-eth1 connects to s1, etc.
      net.addLink(sw[i], sw[j], port1=sj_num, port2=si_num, bw=15, delay='5ms')

  # net.addLink(sw[4], sw[5], port1=6, port2=5, bw=15, delay='5ms')

  # Add link between a host and a switch
  for (h, s) in [(h1, sw[2]), (h2, sw[5]), (h3, sw[5])]:
    h_num = int(h.name[1])
    s_num = int(s.name[1])
    # print("h%d, s%d" % (h_num, s_num))
    net.addLink(h, s, port1=s_num, port2=10+h_num, bw=10, delay='15ms') # s3-eth11 connects to h1, h1-eth3 connects to s3

  # Start each switch and assign it to the controller
  # for s in sw:
  #   s.start([c1])
  
  net.staticArp() # add all-pairs ARP entries to eliminate the need to handle broadcast
  net.start()

  # print "Network connectivity"
  # dumpNetConnections(net)
  # net.pingAll()
  # print(sw[5].intfs)   # print node dict {port# : intf object}
  # print(h1.IP(h1.intfs[3]))   # print IP associated with a specific interface of h1
  # print(sw[5].ports)   # print node dict {intf object : port#}

#   # setup bidirectional path between h1 and h2
#   sw[0].cmd('ovs-ofctl add-flow s3 in_port=3,dl_type=0x0800,nw_src='+h1.IP()+',nw_dst='+h2.IP()+',actions=output:1')
#   sw[0].cmd('ovs-ofctl add-flow s1 in_port=1,dl_type=0x0800,nw_src='+h1.IP()+',nw_dst='+h2.IP()+',actions=output:4')
#   sw[0].cmd('ovs-ofctl add-flow s6 in_port=1,dl_type=0x0800,nw_src='+h1.IP()+',nw_dst='+h2.IP()+',actions=output:3')
#   sw[0].cmd('ovs-ofctl add-flow s6 in_port=3,dl_type=0x0800,nw_src='+h2.IP()+',nw_dst='+h1.IP()+',actions=output:1')
#   sw[0].cmd('ovs-ofctl add-flow s1 in_port=4,dl_type=0x0800,nw_src='+h2.IP()+',nw_dst='+h1.IP()+',actions=output:1')
#   sw[0].cmd('ovs-ofctl add-flow s3 in_port=1,dl_type=0x0800,nw_src='+h2.IP()+',nw_dst='+h1.IP()+',actions=output:3')
#   # setup bidirectional path between h1 and h3
#   sw[0].cmd('ovs-ofctl add-flow s3 in_port=3,dl_type=0x0800,nw_src='+h1.IP()+',nw_dst='+h3.IP()+',actions=output:2')
#   sw[0].cmd('ovs-ofctl add-flow s2 in_port=1,dl_type=0x0800,nw_src='+h1.IP()+',nw_dst='+h3.IP()+',actions=output:4')
#   sw[0].cmd('ovs-ofctl add-flow s6 in_port=2,dl_type=0x0800,nw_src='+h1.IP()+',nw_dst='+h3.IP()+',actions=output:4')
#   sw[0].cmd('ovs-ofctl add-flow s6 in_port=4,dl_type=0x0800,nw_src='+h3.IP()+',nw_dst='+h1.IP()+',actions=output:2')
#   sw[0].cmd('ovs-ofctl add-flow s2 in_port=4,dl_type=0x0800,nw_src='+h3.IP()+',nw_dst='+h1.IP()+',actions=output:1')
#   sw[0].cmd('ovs-ofctl add-flow s3 in_port=2,dl_type=0x0800,nw_src='+h3.IP()+',nw_dst='+h1.IP()+',actions=output:3')

  CLI(net)  # open command-line interface
  # Start iperf server (-s) in h1
  # h1.cmd('iperf -s &')
  # Run a iperf client on h2 and print the throughput
  # result = h2.cmd('iperf -yc -c ' + h1.IP() + ' -t 2').split(",")[-1] # test for 2 sec, parse the csv row to get the last item (bandwidth in bps)
  # print "Throughput between h1<-->h2: " + str(float(result)/1000000.0) + "Mbps"
  net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
