#!/bin/sh
#
echo "Starting RPI-QL Web server"
sudo python3 rpiqlweb.py >/dev/null 2>&1 &
echo "Web server started"
