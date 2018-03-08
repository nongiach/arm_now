#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from scapy.all import DHCP_am
from scapy.base_classes import Net
import os


def main():
    if os.getuid() != 0:
        print("Start as root plz !!")
        return 1

    dhcp_server = DHCP_am(iface='br0', domain='example.com',
                          pool=Net('192.168.122.20-254'),
                          network='192.168.122.0/24',
                          gw='192.168.122.1',
                          renewal_time=600, lease_time=3600)
    dhcp_server()

if __name__ == "__main__":
    main()

# https://bugs.busybox.net/show_bug.cgi?id=3979
# http://www.ingmarverheij.com/configure-hostname-via-dhcp/
