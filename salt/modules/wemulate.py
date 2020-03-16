__virtualname__ = 'wemulate'

def __virtual__():
    return __virtualname__

def set_delay(interface_name, delay):
    command = f'sudo tc qdisc add dev {interface_name} root netem delay {delay}ms'
    __salt__['cmd.run'](command)
    return f'Delay of {delay}ms was successfully added to interface {interface_name}'

def remove_delay(interface_name):
    command = f'sudo tc qdisc del dev {interface_name} root netem delay 0ms'
    __salt__['cmd.run'](command)
    return f'Delay was successfully removed from interface {interface_name}'
