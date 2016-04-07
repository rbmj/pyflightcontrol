#!/bin/bash

if [ $# -ne 2 ]; then
    echo "USAGE: $0 pi_iface inet_iface" 1>&2
    exit 1
fi
if [ `whoami` != root ]; then
    echo "Must be root" 1>&2
    exit 1
fi

sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -o $2 -j MASQUERADE
iptables -A FORWARD -i $2 -o $1 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $1 -o $2 -j ACCEPT

