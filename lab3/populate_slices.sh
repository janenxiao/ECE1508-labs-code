#!/bin/bash

# blue slice handles tcp packets (nw_proto=6) with transport-layer source (tp_src=80) or destination port (tp_dst=80) number set to 80
fvctl -n add-flowspace bfs-http all 2 nw_proto=6,tp_src=80 blue=7
fvctl -n add-flowspace bfs-http all 2 nw_proto=6,tp_dst=80 blue=7

# red slice handles all other packets
fvctl -n add-flowspace rfs-nonHttp all 1 all red=7