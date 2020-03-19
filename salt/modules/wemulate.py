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
