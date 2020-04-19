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

__virtualname__ = 'wemulate'

def __virtual__():
    return __virtualname__


# ----------------------------------------------------------------------------------------------------------------------
# callable functions
# ----------------------------------------------------------------------------------------------------------------------


def set_delay(interface_name, delay):
    '''
    Return string "Delay of <delay>ms was successfully added to interface <interface name>"
    CLI Example:
    .. code-block:: bash
        salt '*' wemulate.set_delay ens123 100
    Example output:
    .. code-block:: python
        Delay of 100ms was successfully added to interface ens123
    :param dest:
    :return:
    '''

    command = f'sudo tc qdisc add dev {interface_name} root netem delay {delay}ms'
    __salt__['cmd.run'](command)
    return f'Delay of {delay}ms was successfully added to interface {interface_name}'


def remove_delay(interface_name):
    '''
    Return string "Delay was successfully removed from interface <interface name>"
    CLI Example:
    .. code-block:: bash
        salt '*' wemulate.remove_delay ens123
    Example output:
    .. code-block:: python
         Delay was successfully remove from interface ens123
    :param dest:
    :return:
    '''
    command = f'sudo tc qdisc del dev {interface_name} root netem delay 0ms'
    __salt__['cmd.run'](command)
    return f'Delay was successfully removed from interface {interface_name}'


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