#!/bin/bash
fvctl -n add-slice blue tcp:127.0.0.1:8000 admin@blue
fvctl -n add-slice red tcp:127.0.0.1:9000 admin@red