#!/bin/bash

#this script sends a timestamped email containing connection information
#to a pre-determined receiver address
#NOTE: in order for this to work the machine it runs on needs to be configured for sending email
#either directly or through a proxy
#I'm personally using wireguard for this
#as an example of how this might be set up with a proxy email server (assuming the email server itself is configured)
#here are a couple lines from my /etc/rc.local:
#	
#iptables -t nat -A OUTPUT -p tcp '!' -d 127.0.0.1/32 --dport 25 -j DNAT --to-destination <wireguard-subnet-email-server-ip>:25
#iptables -t nat -A POSTROUTING -p tcp '!' -d 127.0.0.1/32 --dport 25 -j SNAT --to-source <wireguard-subnet-localhost-ip>


recv_addr='neutrak@4srs.org'
ip_addr_info="$(curl https://ip.4srs.org)"
hostname="$(cat /etc/hostname)"
now="$(date +'%Y-%m-%d %R:%S')"

echo "$ip_addr_info" | mail -s "Connection Information for ${hostname} at ${now}" "${recv_addr}"


