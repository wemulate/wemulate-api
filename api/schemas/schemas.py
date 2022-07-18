from typing import List, Dict
from pydantic import BaseModel


class Device(BaseModel):
    mgmt_interfaces: List[Dict]
    logical_interfaces: List[Dict]


class ConnectionBase(BaseModel):
    connection_name: str
    first_logical_interface_id: int
    second_logical_interface_id: int


class ConnectionResponse(ConnectionBase):
    connection_id: int


class Connection(ConnectionBase):
    connection_id: int
    delay: int
    packet_loss: int
    bandwidth: int
    jitter: int
