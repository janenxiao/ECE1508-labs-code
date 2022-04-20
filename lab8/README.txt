Script needs to be run as: sudo bash hw8.sh <Base IP of Openstack REST API>
For example: sudo bash hw8.sh 10.0.2.15
Script needs sudo privilege to change the number of online CPUs

Parameters in the script that can be tuned:
numMonitor=40           # number of times to call Collect (to monitor stats) after calling Create or Destroy
interval_mpstat=2       # interval (seconds) for CPU stats in each Collect
max_numservers=4        # maximum number of VMs to create in an iteration
max_numcpu=2            # number of CPUs available for testing
timeTest=$((7*60))      # duration (seconds) for testing before reporting on final stats, default is 7 min

numMonitor*interval_mpstat  is roughly the time (seconds) to monitor stats after calling Create or Destroy each time

Script prints the following statistics in the end:
- CPU% per core for creating a VM
- Memory usage (MB) for creating a VM
- CPU% per core for deleting a VM
- Memory usage (MB) for deleting a VM (negative if usage decreased)
It also writes a line in statistics.csv each time calling Collect

Script performs the following tasks:
- Create a network named RED, create a subnet in RED network
- Get flavor_id of 'm1.nano', get an image_id
- Start with only 1 active CPU
- While <timeTest> is not reached:
    - Collect average CPU per core (avgCPU) and memory usage (memUse) as baseline
    - Create a random number num_servers (between 1 and <max_numservers>) of VMs in Red network
    - Call Collect <numMonitor> times, each time Collect writes a line in statistics.csv, recording
      avgCPU in the last <interval_mpstat> seconds and memUse
    - The largest avgCPU and memUse are used to compare with baseline, the average CPU per core for
      creating a VM is calculated as consumed_avgCPU = (largest_avgCPU - baseline_avgCPU) / num_servers
    
    - Collect average CPU per core (avgCPU) and memory usage (memUse) as baseline
    - Delete the VMs created
    - Call Collect <numMonitor> times as above
    - The largest avgCPU and the smallest memUse are used to compare with baseline, the memory usage
      for destroying a VM is calculated as consumed_memUse = (smallest_memUse - baseline_memUse) / num_servers,
      it is negative because memory usage decreases after deleting the VMs
    
    - Write a line in statistics.csv recording num_CPU, num_servers, consumed_avgCPU and consumed_memUse
      for creating and deleting a VM in this iteration
    - Activate one more CPU, if num_CPU has reached <max_numcpu>, go back to 1 active CPU again

- Print average consumed_avgCPU and consumed_memUse for creating and deleting a VM across iterations
- Delete the RED network


Note:
- consumed_avgCPU can be very small with only 1 active CPU, when baseline_avgCPU is already close to 100%,
  the maximum it can rise to is 100%, the difference (largest_avgCPU - baseline_avgCPU) is small, and even
  smaller after dividing by num_servers
