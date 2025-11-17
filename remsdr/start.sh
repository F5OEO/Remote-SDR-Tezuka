#!/bin/bash
if [ ! -f /remsdr/data/selfsigned.key ] || [ ! -f /remsdr/data/selfsigned.crt ]; then
    echo "Creating self signed key"
    export CAROOT=/remsdr/data
    mkcert -install
    mkcert -cert-file /remsdr/data/selfsigned.crt -key-file /remsdr/data/selfsigned.key "127.0.0.1"
fi
echo "Starting app"
export NODE_PATH=/usr/local/lib/node_modules/ && nodejs /remsdr/Radio_Server.js

