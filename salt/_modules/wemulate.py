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
import yaml

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
        if interface_matches_criteria(name):
            interfaces_list.append(name)
    return interfaces_list

def interface_matches_criteria(interface_name):
    with open('/etc/wemulate/config.yaml') as file:
        config = yaml.full_load(file)
    if interface_name.startswith(("eth", "en")) and interface_name not in config['management_interfaces']:
        return True
    return False

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

    netem_command = add_delay(netem_command, parameters)
    netem_command = add_jitter(netem_command, parameters)
    netem_command = add_packet_loss(netem_command, parameters)
    netem_command = add_duplication(netem_command, parameters)
    netem_command = add_corruption(netem_command, parameters)

    if any(parameter in parameters for parameter in ("delay", "jitter", "packet_loss", "duplication", "corruption")):
        __salt__['cmd.run'](netem_command)
        log.info(netem_command)

    if "bandwidth" in parameters:
        bw_result = add_bandwidth(interface_name, parameters)
        log.info(bw_result)

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
    bandwidth_in_kbit = parameters["bandwidth"] * 1000
    command = f'sudo /home/wemulate/wondershaper/wondershaper -a {interface_name} -u {bandwidth_in_kbit} -d {bandwidth_in_kbit}'
    __salt__['cmd.run'](command)
    return f'bandwidth {parameters["bandwidth"]} on {interface_name} set'

def add_duplication(command, parameters):
    if "duplication" in parameters:
        return command + ' ' + f'duplicate {parameters["duplication"]}%'
    return command

def add_corruption(command, parameters):
    if "corruption" in parameters:
        return command + ' ' + f'corrupt {parameters["corruption"]}%'
    return command

def remove_parameters(interface_name):
    command = f'sudo tc qdisc del dev {interface_name} root'
    __salt__['cmd.run'](command)
    command = f'sudo /home/wemulate/wondershaper/wondershaper -c -a {interface_name}'
    __salt__['cmd.run'](command)
    return f"Successfully removed parameters"
