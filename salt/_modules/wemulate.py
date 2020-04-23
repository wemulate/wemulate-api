# -*- coding: utf-8 -*-
'''
WEmulate - WAN Emulator
===============
Functions which can be used to emulate network traffic.
Module can be used to add different parameters to an interface.
Parameters are packet loss, delay, jitter and bandwith (more will follow)-to unit tests.
:codeauthor: WEmulate Team <severin.dellsperger@hsr.ch> <dominic.gabriel@hsr.ch> <uben.william.broennimann@hsr.ch>> <julian.klaiber@hsr.ch>
:maturity:   new
:depends:    tc
:platform:   unix
'''

import os
import netifaces
from pyroute2 import IPRoute
import logging

__virtualname__ = 'wemulate'
log = logging.getLogger(__name__)

def __virtual__():
    return __virtualname__


# ----------------------------------------------------------------------------------------------------------------------
# callable functions
# ----------------------------------------------------------------------------------------------------------------------

def get_interfaces():
    interfaces_list = []
    for name in netifaces.interfaces():
        if name.startswith(("eth","en")):
            interfaces_list.append(name)
    return interfaces_list


def add_connection(connection_name, interface1_name, interface2_name):
    include_str = 'source /etc/network/interfaces.d/*'
    with open('/etc/network/interfaces', 'a+') as f:
        if not any(include_str == x.rstrip('\r\n') for x in f):
            f.write(include_str + '\n')

    connection_template = f"# Bridge Setup {connection_name}\nauto {connection_name}\niface {connection_name} inet manual\n    bridge_ports {interface1_name} {interface2_name}\n    bridge_stp off\n"

    with open(f"/etc/network/interfaces.d/{connection_name}", "w") as file:
        file.write(connection_template)

    __salt__['cmd.run']("sudo systemctl restart networking.service")
    return connection_template


def remove_connection(connection_name):
    ip = IPRoute()
    x = ip.link_lookup(ifname=connection_name)[0]
    ip.link("set", index=x, state="down")

    __salt__['cmd.run'](f"sudo brctl delbr {connection_name}")

    connection_file = f"/etc/network/interfaces.d/{connection_name}"
    if os.path.exists(connection_file):
        os.remove(connection_file)
    else:
        print("file does not exist")

    return f"Successfully removed connection {connection_name}"


def set_parameters(interface_name, parameters):
    base_command = f'sudo tc qdisc add dev {interface_name} '
    netem_command = base_command + 'root handle 1: netem'
    tbf_command = base_command + 'parent 1: handle 2: tbf'

    netem_command = add_delay(netem_command, parameters)
    netem_command = add_jitter(netem_command, parameters)
    netem_command = add_packetloss(netem_command, parameters)

    if any(parameter in parameters for parameter in ("delay", "jitter", "packet_loss")):
        __salt__['cmd.run'](netem_command)
        log.info(netem_command)

    if "bandwidth" in parameters:
        log.info(add_bandwidth(interface_name, parameters))

    return "Successfully added parameters"


def add_delay(command, parameters):
    if "delay" in parameters:
        return command + ' ' + f'delay {parameters["delay"]}ms'
    return command


def add_jitter(command, parameters):
    if "jitter" in parameters:
        jitter = parameters["jitter"] / 2
        if "delay" in parameters:
            return command + ' ' + f'{jitter}ms distribution normal'
        else:
            return command + ' ' + f'delay 0.1ms {jitter}ms distribution normal'
    return command


def add_packet_loss(command, parameters):
    if "packet_loss" in parameters:
        return command + ' ' + f'loss {parameters["packet_loss"]}%'
    return command


def add_bandwidth(interface_name, parameters):
    __salt__['cmd.run']('sudo modprobe ifb numifbs=1')
    __salt__['cmd.run']('sudo ip link set dev ifb0 up')
    command = f'sudo tc qdisc add dev {interface_name} handle ffff: ingress'
    __salt__['cmd.run'](command)
    command = f'sudo tc filter add dev {interface_name} parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0'
    __salt__['cmd.run'](command)
    __salt__['cmd.run']('sudo tc qdisc add dev ifb0 root handle 2: htb')
    comand = 'sudo tc class add dev ifb0 parent 2: classid 2:1 htb rate {parameters["bandwidth"]}kbit'
    __salt__['cmd.run'](command)
    __salt__['cmd.run']('sudo tc filter add dev ifb0 protocol ip parent 2: prio 1 u32 match ip src 0.0.0.0/0 flowid 2:')
    return f'bandwidth {parameters["bandwidth"]} on {interface_name} set'


def remove_parameters(interface_name):
    command = f'sudo tc qdisc del dev {interface_name} root'
    __salt__['cmd.run'](command)
    command = f'tc qdisc del dev {interface_name} ingress'
    __salt__['cmd.run'](command)
    return f"Successfully removed parameters"
