# -*- coding: utf-8 -*-
'''
WEmulate - WAN Emulator
===============
Functions which can be used to emulate network traffic.
Module can be used to add different parameters to an interface.
Parameters are packet loss, delay, jitter and bandwith (more will follow)-to unit tests.
:codeauthor: WEmulate Team <severin.dellsperger@hsr.ch> <dominic.gabriel@hsr.ch> <ruben.william.broennimann@hsr.ch>> <julian.klaiber@hsr.ch>
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
# helper functions
# ----------------------------------------------------------------------------------------------------------------------

def _execute_in_shell(command):
    __salt__['cmd.run'](command)

def _interface_matches_criteria(interface_name):
    with open('/etc/wemulate/config.yaml') as file:
        config = yaml.full_load(file)
    if interface_name.startswith(("eth", "en")) and interface_name not in config['management_interfaces']:
        return True
    return False

# ----------------------------------------------------------------------------------------------------------------------
# callable functions
# ----------------------------------------------------------------------------------------------------------------------
BRIDGE_CONFIG_PATH = '/etc/network/interfaces.d'
ip = IPRoute()

def get_interfaces():
    interfaces_list = []
    for name in netifaces.interfaces():
        if _interface_matches_criteria(name):
            interfaces_list.append(name)
    return interfaces_list


def get_management_ip():
    with open('/etc/wemulate/config.yaml') as file:
        config = yaml.full_load(file)
    if config['management_interfaces']:
        interface_name = config['management_interfaces'][0]
    else:
        return '0.0.0.0'

    index_list = ip.link_lookup(ifname=interface_name)
    if index_list:
        interface = ip.get_addr(index=index_list[0])
        interface_ip = interface[0]['attrs'][0][1]
    else:
        interface_ip = '10.0.0.10'
    return interface_ip


def add_connection(connection_name, interface1_name, interface2_name):
    INTERFACE_CONFIG_PATH = '/etc/network/interfaces'

    with open(INTERFACE_CONFIG_PATH, 'r+') as interfaces_config_file:
        if BRIDGE_CONFIG_PATH not in interfaces_config_file.read():
            interfaces_config_file.write(f'source {BRIDGE_CONFIG_PATH}/*\n')

    connection_template = f"# Bridge Setup {connection_name}\nauto {connection_name}\niface {connection_name} inet manual\n    bridge_ports {interface1_name} {interface2_name}\n    bridge_stp off\n"

    if not os.path.exists('BRIDGE_CONFIG_PATH'):
        os.makedirs('BRIDGE_CONFIG_PATH')

    with open(f"{BRIDGE_CONFIG_PATH}/{connection_name}", "w") as connection_file:
        connection_file.write(connection_template)

    _execute_in_shell("sudo systemctl restart networking.service")
    return connection_template


def remove_connection(connection_name):
    ip.link("set", index=ip.link_lookup(ifname=connection_name)[0], state="down")
    _execute_in_shell(f"sudo brctl delbr {connection_name}")

    connection_file = f"{BRIDGE_CONFIG_PATH}/{connection_name}"
    if os.path.exists(connection_file):
        os.remove(connection_file)

    return f"Successfully removed connection {connection_name}"


def set_parameters(interface_name, parameters):
    command = f'tcset {interface_name} '
    mean_delay = 0
    if parameters:
        if 'delay' in parameters:
            mean_delay = parameters['delay']
            if 'jitter' not in parameters:
                command += add_delay_command(mean_delay)
        if 'jitter' in parameters:
            command += add_jitter_command(mean_delay, parameters['jitter'])
        if 'packet_loss' in parameters:
            command += add_packet_loss_command(parameters['packet_loss'])
        if 'bandwidth' in parameters:
            command += add_bandwidth_command(parameters['bandwidth'])
        if 'duplication' in parameters:
            command += add_duplication_command(parameters['duplication'])
        if 'corruption' in parameters:
            command += add_corruption_command(parameters['corruption'])

        log.info(command)
        return _execute_in_shell(command)

def add_delay_command(delay_value):
    return f'--delay {delay_value}ms'

def add_jitter_command(mean_delay, jitter_value):
    return f'--delay {mean_delay}ms --delay-distro {jitter_value}'


def add_packet_loss_command(packet_loss_value):
    return f'--loss {packet_loss_value}%'


def add_bandwidth_command(bandwidth_value):
    return f'--rate {bandwidth_value}Mbps'

def add_duplication_command(duplication_value):
    return f'--duplicate {duplication_value}%'

def add_corruption_command(corruption_value):
    return f'--corrupt {corruption_value}%'

def remove_parameters(interface_name):
    command = f'tcdel {interface_name} --all'
    return _execute_in_shell(command)
