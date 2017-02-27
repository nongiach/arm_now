#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from scapy.all import DHCP_am
from scapy.base_classes import Net

dhcp_server = DHCP_am(iface='virbr0', domain='example.com',
                      pool=Net('192.168.122.0/24'),
                      network='192.168.122.0/24',
                      gw='192.168.122.254',
                      renewal_time=600, lease_time=3600)
dhcp_server()
