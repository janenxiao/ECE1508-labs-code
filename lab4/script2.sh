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

function list_networks {
    local pyscript='import json,sys;obj=json.load(sys.stdin);'
    pyscript+='new_obj={"networks": [dict((k, network[k]) for k in ["id","name","status"]) for network in obj["networks"]]};print(json.dumps(new_obj,indent=4))'

    networks_json=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "$Network_BASEURL/v2.0/networks" | python -c "$pyscript")
    networks_json=${networks_json:1:-1}   # remove beginning and ending curly brackets
    # "networks": [{..},{..}]
}

function list_router_ports {
    local routers_result=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "$Network_BASEURL/v2.0/routers" | jq '[.routers[] | {name, id}]')
    # echo $routers_result | python -m json.tool
    routers_json=''
    for k in $(jq 'keys | .[]' <<< "$routers_result"); do
        router_id=$(jq ".[$k].id" <<< "$routers_result");
        router_id=${router_id//\"}      # remove quotes around <router_id>
        # echo "$router_id"
        ports_result=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "$Network_BASEURL/v2.0/ports?device_id=$router_id" | jq '[.ports[] | {id, device_id, network_id, status}]')
        # echo "$ports_result" | python -m json.tool

        router_obj=$(jq ".[$k]" <<< "$routers_result")    # replace closing '}' with ',' from router object
        router_obj="${router_obj/%'}'/,}"
        # echo "$router_obj"
        routers_json+="$router_obj \"ports\": $ports_result},"   # add "ports" list to router object
    done
    # echo "$routers_json"
    routers_json="\"routers\": [${routers_json%,}]"    # remove last ',' then construct "routers" list
    # echo $routers_json    # "routers": [{..},{..}]
}

function list_servers {
    local pyscript='import json,sys;obj=json.load(sys.stdin);'
    pyscript+='new_obj={"servers": [dict((k, server[k]) for k in ["id","name","status"]) for server in obj["servers"]]};print(json.dumps(new_obj,indent=4))'
    
    servers_json=$(curl -s -H "X-Auth-Token:$OS_TOKEN" "http://$BASE_IP/compute/v2.1/servers/detail" | python -c "$pyscript")
    servers_json=${servers_json#{}      # remove beginning '{'
    servers_json="${servers_json%'}'}"  # remove ending '}'
    # "servers": [{..},{..}]
}

BASE_IP=$1
Network_BASEURL="http://$BASE_IP:9696"
# OS_TOKEN=$2

get_token
list_networks
list_router_ports
list_servers
echo "{$networks_json, $routers_json, $servers_json}" | python -m json.tool
# echo "{$networks_json, $routers_json, $servers_json}"