from typing import List, Optional
from pydantic import BaseModel


class ManagementInterface(BaseModel):
    ip: Optional[str]
    physical_name: str


class LogicalInterface(BaseModel):
    interface_id: int
    logical_name: str
    physical_name: str


class Device(BaseModel):
    mgmt_interfaces: List[ManagementInterface]
    logical_interfaces: List[LogicalInterface]


class Parameter(BaseModel):
    delay: int = 0
    packet_loss: int = 0
    bandwidth: int = 0
    jitter: int = 0


class ConnectionBase(BaseModel):
    connection_name: str
    first_logical_interface_id: int
    second_logical_interface_id: int


class Connection(ConnectionBase):
    incoming: Parameter
    outgoing: Parameter


class ConnectionComplete(Connection):
    connection_id: int


class ConnectionList(BaseModel):
    connections: List[ConnectionComplete]
