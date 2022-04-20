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
    local network_type=$2
    local router_external=$3

    if [[ "$network_type" == "flat" ]]
    then
    data="{
        \"network\": {
            \"name\": \"$name\",
            \"admin_state_up\": true,
            \"shared\": false,
            \"provider:network_type\": \"$network_type\",
            \"provider:physical_network\": \"public\",
            \"router:external\": $router_external
        }
    }"
    else    # "$network_type" == "vxlan"
    data="{
        \"network\": {
            \"name\": \"$name\",
            \"admin_state_up\": true,
            \"shared\": false,
            \"provider:network_type\": \"$network_type\",
            \"router:external\": $router_external
        }
    }"
    fi
    
    network_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/networks" | jq '.network.id')
    # curl -i -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/networks"
    # network_id=${network_id:1:-1}   # remove quotes
    echo "Created network $name, id: $network_id"

    # create subnet
    local subnet_cidr=$4
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

function create_router {
    # create router
    local name=$1
    data="{
        \"router\": {
            \"name\": \"$name\",
            \"external_gateway_info\": {
                \"network_id\": ${publicNet[0]},
                \"enable_snat\": true,
                \"external_fixed_ips\": [
                    {
                        \"ip_address\": \"172.24.4.6\",
                        \"subnet_id\": ${publicNet[1]}
                    }
                ]
            }
        }
    }"
    # router_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/routers" | jq '.router.id')
    local router_result=$(curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/routers")
    echo "Create router returns: $router_result"
    router_id=$(echo "$router_result" | jq '.router.id')
    echo "Created router $name, id: $router_id"

    # add router interface to RED network
    data="{
        \"subnet_id\": ${redNet[1]}
    }"
    # ${router_id//\"} removes quotes around <router_id>
    curl -s -X PUT -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/routers/${router_id//\"}/add_router_interface" | python -mjson.tool
    echo "Added router interface to red subnet ${redNet[1]}"

    # add router interface to BLUE network
    data="{
        \"subnet_id\": ${blueNet[1]}
    }"
    curl -s -X PUT -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/routers/${router_id//\"}/add_router_interface" | python -mjson.tool
    echo "Added router interface to blue subnet ${blueNet[1]}"

    # add router interface to PUBLIC network
    data="{
        \"subnet_id\": ${publicNet[1]}
    }"
    curl -s -X PUT -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/routers/${router_id//\"}/add_router_interface" | python -mjson.tool
    echo "Added router interface to public subnet ${publicNet[1]}"
}

function update_subnet {
    local subnet_id=$1

    data="{
        \"subnet\": {
            \"gateway_ip\": \"172.24.4.6\"
        }
    }"
    curl -s -X PUT -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/subnets/${subnet_id//\"}" | python -mjson.tool
}

function update_router {
    local router_id=$1

    data="{
        \"router\": {
            \"admin_state_up\": false
        }
    }"
    curl -s -X PUT -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/routers/${router_id//\"}" | python -mjson.tool
}

function remove_router_iface {
    local router_id=$1
    local port_id=$2

    data="{
        \"port_id\": $port_id
    }"
    curl -s -X PUT -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/routers/${router_id//\"}/remove_router_interface" | python -mjson.tool
}

function delete_router {
    local router_id=$1
    local ports=$2      # format: (port_id port_id), contains ids of ports that were added to router

    for port_id in "${ports[@]}"; do
        remove_router_iface "$router_id" "$port_id"
    done
    curl -i -X DELETE -H "X-Auth-Token:$OS_TOKEN" "$Network_BASEURL/v2.0/routers/${router_id//\"}"
}

function delete_server {
    local server_id=$1

    curl -i -X DELETE -H "X-Auth-Token:$OS_TOKEN" "$http://$BASE_IP/compute/v2.1/servers/${server_id//\"}"
}

function get_flavor_id {
    local flavor_name=$1
    flavor_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/compute/v2.1/flavors" | jq ".flavors[] | select(.name==\"$flavor_name\") | .id")
    echo "flavor $flavor_name has id: $flavor_id"
}

function create_server {
    local name=$1
    local network_uuid=$2
    # local server_id=$3

    data="{
        \"server\": {
            \"name\": \"$name\",
            \"flavorRef\": $flavor_id,
            \"imageRef\": $image_id,
            \"networks\": [{
                \"uuid\": $network_uuid
            }]
        }
    }"
    # curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "http://$BASE_IP/compute/v2.1/servers" | python -m json.tool
    server_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "http://$BASE_IP/compute/v2.1/servers" | jq '.server.id')
    echo "Created server $name, id: $server_id"
}

function get_server_port {  # get port_id of server
    local server_id=$1

    # curl -s -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/compute/v2.1/servers/${server_id//\"}/os-interface"
    port_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/compute/v2.1/servers/${server_id//\"}/os-interface" | jq '.interfaceAttachments[0].port_id')
    echo "Server $name has port id: $port_id"
}

function create_floatingip {
    local port_id=$1
    local network_id=$2
    local subnet_id=$3

    data="{
        \"floatingip\": {
            \"floating_network_id\": $network_id,
            \"port_id\": $port_id,
            \"subnet_id\": $subnet_id
        }
    }"
    curl -s -H "X-Auth-Token:$OS_TOKEN" -H 'Content-Type: application/json' -d "$data" "$Network_BASEURL/v2.0/floatingips" | python -mjson.tool
}

BASE_IP=$1
Network_BASEURL="http://$BASE_IP:9696"
# OS_TOKEN=$2

# Note all id variables have format "<id>", i.e. they include double quotes
# redNet and blueNet have format ($network_id $subnet_id)
# redServer and blueServer have format ($server_id $port_id)

get_token
create_network RED vxlan false '192.168.1.0/24'
redNet=($network_id $subnet_id)
echo 'redNET: '
printf "%s " "${redNet[@]}"
create_network BLUE vxlan false '10.0.0.0/24'
blueNet=($network_id $subnet_id)
echo 'blueNET: '
printf "%s " "${blueNet[@]}"
create_network PUBLIC flat true '172.24.4.0/24'
publicNet=($network_id $subnet_id)
echo 'publicNET: '
printf "%s " "${publicNet[@]}"

# redNet=('"f2badcde-af6f-4e12-99a7-4ce66ee273e4"' '"dd22c239-cfc0-49ad-8381-b18a4c72a390"')
# blueNet=('"bf40e3cb-a580-4b3c-8fd9-48cb3ba4f148"' '"82dcddc1-4fab-4695-b4f0-fc5be434c96e"')
# publicNet=('"a2536b5c-79fb-41bb-8ead-530abf56cf84"' '"6ec364e6-974b-4e3d-b2b2-5ef618df9808"')

# # get flavor id for VMs
get_flavor_id 'm1.nano'
# flavor_id='"42"'

# get image id for VMs
image_id=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/image/v2/images" | jq '.images[0].id')
echo "image_id: $image_id"
# image_id='"aaab4dfd-8d9c-409e-a821-a0137e49e869"'

create_server Red-server ${redNet[0]}
# servers_id=($server_id)
redServer=($server_id)
create_server Blue-server ${blueNet[0]}
# create_server Blue-server '"591c9d48-3169-44b5-a643-8886749642bd"'
# servers_id+=($server_id)
blueServer=($server_id)
create_server Public-server ${publicNet[0]}
# create_server Public-server '"4aa96f4c-0182-4456-8c91-1c96914940b2"' '"4eb28952-c76d-4200-b2e2-708686ce82e8"'
# servers_id+=($server_id)
publicServer=($server_id $port_id)

create_router MyGateway

# redServer=('"51f789a2-2de9-4927-a20b-eee01835a657"' '"844e9379-e6dd-471c-b828-9cfc4daf55d8"')
# blueServer=('"9bfed727-c1f8-491e-b3cf-7548e2d99bdd"' '"f730acce-cfad-4efe-bb0b-7a230bc0b78e"')

get_server_port ${redServer[0]}
redServer+=($port_id)
get_server_port ${blueServer[0]}
blueServer+=($port_id)
get_server_port ${publicServer[0]}
publicServer+=($port_id)

echo "Creating floating ip for Red-server"
create_floatingip ${redServer[1]} ${publicNet[0]} ${publicNet[1]}
echo "Creating floating ip for Blue-server"
create_floatingip ${blueServer[1]} ${publicNet[0]} ${publicNet[1]}

# update_router '"e827e76f-aa44-4c1d-9342-c9f99e6ee2be"'
# update_subnet '"6ec364e6-974b-4e3d-b2b2-5ef618df9808"'
# remove_router_iface '"e827e76f-aa44-4c1d-9342-c9f99e6ee2be"' '"60a7b1f4-647d-4efa-8ff6-a964ae3f2116"'
# delete_router '"9c14d232-eed5-4aef-a711-fcfa466d7e29"' ('"09fab1a1-8b96-4673-bbb2-888c97713986"' '"d486ca93-2f4b-4e84-9771-06f558ea5490"')