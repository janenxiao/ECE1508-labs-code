function get_token {
    data='{ 
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": "admin",
                        "domain": { "id": "default" },
                        "password": "secret"
                    }
                }
            },
            "scope": {
                "project": {
                    "name": "admin",
                    "domain": { "id": "default" }
                }
            }
        }
    }'
    local token_result=$(curl -i -H "Content-Type: application/json" -d "$data" "http://$BASE_IP/identity/v3/auth/tokens" | grep "X-Subject-Token")
    echo "$token_result"
    token_result=${token_result#X-Subject-Token: }  # remove 'X-Subject-Token: ' at the beginning
    export OS_TOKEN=${token_result//$'\015'}        # remove end-of-line character (carriage return)
}

function create_network {
    # create network
    local name=$1

    # create private network
    data="{
        \"network\": {
            \"name\": \"$name\",
            \"admin_state_up\": true,
            \"shared\": false,
            \"provider:network_type\": \"vxlan\",
            \"router:external\": false
        }
    }"
    
    network_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/networks" | jq '.network.id')
    # curl -i -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/networks"
    # network_id=${network_id:1:-1}   # remove quotes
    echo "Created network $name, id: $network_id"

    # create subnet
    local subnet_cidr=$2
    data="{
        \"subnet\": {
            \"network_id\": $network_id,
            \"name\": \"${name}-sub\",
            \"ip_version\": 4,
            \"cidr\": \"$subnet_cidr\",
            \"enable_dhcp\": true
        }
    }"
    subnet_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/subnets" | jq '.subnet.id')
    echo "Created subnet $subnet_cidr, id: $subnet_id"
}

function delete_network {
    local network_id=$1
    local subnet_id=$2

    # delete subnet
    curl -s -X DELETE -H "X-Auth-Token:$OS_TOKEN" "$Network_BASEURL/v2.0/subnets/${subnet_id//\"}"
    echo "Deleted subnet, id: $subnet_id"
    # delete network
    curl -s -X DELETE -H "X-Auth-Token:$OS_TOKEN" "$Network_BASEURL/v2.0/networks/${network_id//\"}"
    echo "Deleted network, id: $network_id"
}

function get_flavor_id {
    local flavor_name=$1
    flavor_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/compute/v2.1/flavors" | jq ".flavors[] | select(.name==\"$flavor_name\") | .id")
    echo "flavor $flavor_name has id: $flavor_id"
}

function Create {
    local name=$1
    local network_uuid=$2
    local max_num_servers=$3

    # create a random number of servers
    num_servers=$((1 + $RANDOM % $max_num_servers))    # 1 <= num_servers <= max_num_servers
    # num_servers=$max_num_servers
    echo "Number of servers: $num_servers"

    data="{
        \"server\": {
            \"name\": \"$name\",
            \"flavorRef\": $flavor_id,
            \"imageRef\": $image_id,
            \"networks\": [{
                \"uuid\": $network_uuid
            }],
            \"min_count\": \"$num_servers\"
        }
    }"

    echo "Creating $num_servers server(s)"
    # curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "http://$BASE_IP/compute/v2.1/servers" | python -m json.tool
    server_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "http://$BASE_IP/compute/v2.1/servers" | jq '.server.id')
    # echo "Created server $name, id: $server_id"
}

function Destroy {
    local num_cpu=$1
    
    # collect stats before VM destruction as baseline
    Collect $num_cpu
    base_cpuUtil=$(echo $stat_row | awk '{print $2}')
    base_memUse=$(echo $stat_row | awk '{print $3}')
    # echo "################ base_cpuUtil: $base_cpuUtil base_memUse: $base_memUse"

    max_cpuUtil=0
    min_memUse=$base_memUse

    # delete VMs
    servers_result=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/compute/v2.1/servers" | jq '[.servers[] | {name, id}]')
    local num_servers=$(jq 'length' <<< "$servers_result")
    for k in $(jq 'keys | .[]' <<< "$servers_result"); do
        server_id=$(jq ".[$k].id" <<< "$servers_result");
        server_id=${server_id//\"}      # remove quotes around <router_id>
        echo "Deleting server, id: $server_id"
        
        curl -s -X DELETE -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/compute/v2.1/servers/$server_id"
    done

    # monitor stats after VM destruction
    for (( i=0; i < $numMonitor; i++ )); do
        Collect $num_cpu
        # update max_cpuUtil and min_memUse if cpuUtil increased or memUse decreased
        max_cpuUtil=$(echo $stat_row | awk -v max="$max_cpuUtil" '{print ($2 > max) ? $2 : max}')
        min_memUse=$(echo $stat_row | awk -v min="$min_memUse" '{print ($3 < min) ? $3 : min}')

        # if (( $i % 10 == 0 )); then
        #     mpstat -P ALL 1 1
        # fi
        # sleep $timeMonitor
    done
    # echo "################ max_cpuUtil: $max_cpuUtil min_memUse: $min_memUse"
    # average cpu_util and mem_usage for destroying a VM
    cpuUtil_destroy=$(echo "$max_cpuUtil $base_cpuUtil" | awk -v num=$num_servers '{ print ($1-$2)/num }')
    memUse_destroy=$(echo "$min_memUse $base_memUse" | awk -v num=$num_servers '{ print ($1-$2)/num }')
    # echo "################ cpuUtil_destroy: $cpuUtil_destroy memUse_destroy: $memUse_destroy"

    # # destroy_cpu_mem=${destroy_cpu_mem%$'\n'}    # remove '\n' at the end of destroy_cpu_mem
    # # cpu_mem_destroy=$(echo "$destroy_cpu_mem" | awk '{ numvm++; for (i=1;i<=2;i++){ a[i]+=$i } } END {print a[1]/numvm " " a[2]/numvm }')
}

function Collect {
    local num_cpu=$1
    # mpstat -P ALL 2 1     # get report on CPU stats for an interval of 2 seconds (will get 2 reports, one initial, one after 2 seconds)
    local cpu_util=$(mpstat -P ALL $interval_mpstat 1 | awk -v numcpu=$num_cpu 'NR > 4 && NR <= 4+numcpu {time=$1; cpuUtil += $4+$6} END {print time " " cpuUtil/numcpu}')

    # free -m
    local mem_use=$(free -m | awk 'NR == 2 {print $3}')
    stat_row="$cpu_util $mem_use"
    echo "$stat_row" >> statistics.csv     # append to file
}

function Change {
    local cpuX=$1   # index of target cpu, e.g. 0, 1
    local online_state=$2    # 0 for disable, 1 for enable

    sudo sh -c "echo -n $online_state > /sys/devices/system/cpu/cpu${cpuX}/online"
}

# set <num_activeCPU> CPUs to be active, deactivate the rest
function set_num_activeCPU {
    local num_activeCPU=$1      # number of CPUs to activate

    for (( i=1; i < $max_numcpu; i++ )); do
        if (( $i < $num_activeCPU )); then
            Change $i 1
        else
            Change $i 0
        fi
    done
}

################ run script: sudo bash hw8.sh 10.0.2.15 ################
BASE_IP=$1
Network_BASEURL="http://$BASE_IP:9696"
OS_TOKEN=$2

# Note all id variables have format "<id>", i.e. they include double quotes
# redNet has format ($network_id $subnet_id)

################ Create a network ################
get_token
create_network RED '192.168.1.0/24'
redNet=($network_id $subnet_id)
sleep 5     # wait for network to become active
# # echo 'redNET: '
# # printf "%s " "${redNet[@]}"
# # redNet=('"aaf5a072-9f99-456e-9de6-2f8786785ede"' '"4c551f93-b2b0-4e18-9daf-5b443762d0be"')

# # get flavor id for VMs
get_flavor_id 'm1.nano'
# # flavor_id='"42"'

# get image id for VMs
image_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/image/v2/images" | jq '.images[0].id')
echo "image_id: $image_id"
# # image_id='"aaab4dfd-8d9c-409e-a821-a0137e49e869"'


################ Parameters ################
numMonitor=40           # number of times to monitor statistics (call Collect) after running Create or Destroy
# timeMonitor=0           # seconds to sleep after calling Collect each time
interval_mpstat=2       # seconds to report on CPU stats in each Collect
max_numservers=4        # maximum number of VMs to create in an iteration
max_numcpu=2            # number of CPUs available
timeTest=$((7*60))      # seconds to keep creating & destroying VMs before reporting on final stats


# each line in stats_cpu_mem has form "<cpu_util for creating a VM> <mem_usage for creating a VM> <cpu_util for destroying a VM> <mem_usage for destroying a VM>"
stats_cpu_mem=''
startTime=$SECONDS
num_cpu=1

# each line in statistics.csv has form "<time> <cpu_util> <mem_usage>"
echo "time cpu_util mem_usage" > statistics.csv     # write to file, overwrite if already exists

set_num_activeCPU $num_cpu     # start with only 1 active CPU, deactivate the rest

################ Test script ################
while (( $SECONDS-$startTime < $timeTest )); do
    # # prepare to Create VMs
    max_cpuUtil=0
    max_memUse=0

    # collect stats before VM creation as baseline
    Collect $num_cpu
    base_cpuUtil=$(echo $stat_row | awk '{print $2}')
    base_memUse=$(echo $stat_row | awk '{print $3}')
    # echo "################ base_cpuUtil: $base_cpuUtil base_memUse: $base_memUse"
    # create multiple VMs
    Create Red-server ${redNet[0]} $max_numservers
    # monitor stats after VM creation
    for (( i=0; i < $numMonitor; i++ )); do
        Collect $num_cpu
        # printf 'Collected %d times\n' $(($i+1))

        # update max_cpuUtil and max_memUse if collected cpuUtil and memUse is larger
        max_cpuUtil=$(echo $stat_row | awk -v max="$max_cpuUtil" '{print ($2 > max) ? $2 : max}')
        memUse=$(echo $stat_row | awk '{print $3}')
        if (( $memUse > $max_memUse )); then
            max_memUse=$memUse
        fi

        # if (( $i % 10 == 0 )); then
        #     mpstat -P ALL 1 1
        # fi
        # sleep $timeMonitor
    done
    # echo "################ max_cpuUtil: $max_cpuUtil max_memUse: $max_memUse"
    # average cpu_util and mem_usage for creating a VM in this iteration
    cpuUtil_create=$(echo "$max_cpuUtil $base_cpuUtil" | awk -v num="$num_servers" '{ print ($1-$2)/num }')
    memUse_create=$(echo "$max_memUse $base_memUse" | awk -v num="$num_servers" '{ print ($1-$2)/num }')
    # echo "################ cpuUtil_create: $cpuUtil_create memUse_create: $memUse_create"

    # # prepare to Destroy VMs
    Destroy $num_cpu

    # average cpu_util and mem_usage for destroying a VM in this iteration
    # cpu_mem_destroy has form "<cpu_util> <mem_usage>"
    cpu_mem_destroy="$cpuUtil_destroy $memUse_destroy"
    # echo "################ cpu_mem_destroy: $cpu_mem_destroy"

    stats_cpu_mem+="$cpuUtil_create $memUse_create $cpu_mem_destroy"$'\n'

    echo "numCPU:$num_cpu numVM:$num_servers $cpuUtil_create $memUse_create $cpu_mem_destroy" >> statistics.csv    # append to file
    echo "number of CPUs: $num_cpu"$'\t'"number of VMs: $num_servers"$'\t'"CPU, Memory for Create: $cpuUtil_create, $memUse_create"$'\t'"CPU, Memory for Destroy: $cpuUtil_destroy, $memUse_destroy"
    
    if (( $num_cpu +1 <= $max_numcpu )); then
        Change $num_cpu 1               # activate the CPU with index num_cpu
        num_cpu=$((num_cpu+1))
    elif (( $max_numcpu > 1 )); then    # if more than 1 CPU available
        set_num_activeCPU 1             # go back to only 1 active CPU, deactivate the rest
        num_cpu=1
    fi
    echo "new numCPU: $num_cpu"
    
    # sleep $timeMonitor
    sleep $interval_mpstat
done

stats_cpu_mem=${stats_cpu_mem%$'\n'}    # remove the last '\n' at the end of string
# calculate average of each column
stats_array=$(echo "$stats_cpu_mem" | awk '{ numrow++; for (i=1;i<=4;i++){ a[i]+=$i } } END { for (i=1;i<=4;i++){ printf "%f ", a[i]/numrow } }')
stats_array=($stats_array)
echo "CPU% per core for creating a VM: ${stats_array[0]}"
echo "Memory usage (MB) for creating a VM: ${stats_array[1]}"
echo "CPU% per core for deleting a VM: ${stats_array[2]}"
echo "Memory usage (MB) for deleting a VM (negative if usage decreased): ${stats_array[3]}"

################ Delete the network ################
delete_network ${redNet[0]} ${redNet[1]}



