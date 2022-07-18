from typing import List, Dict
from fastapi.params import Body
from fastapi.routing import APIRouter
from fastapi import Request
from api.schemas.schemas import ConnectionResponse, Device, Connection, ConnectionBase
import api.core.utils as utils

router = APIRouter(prefix="/v1", tags=["v1"])


@router.get("/device", response_model=Device)
def get_device():
    return {
        "mgmt_interfaces": utils.get_mgmt_interfaces(),
        "logical_interfaces": utils.get_logical_interfaces(),
    }


@router.get("/connections", response_model=Dict)
def get_connections():
    return {"connections": utils.get_all_connections()}


@router.post("/connections", response_model=ConnectionResponse)
def post_connections(connection: ConnectionBase):
    return utils.create_connection(
        connection.connection_name,
        connection.first_logical_interface_id,
        connection.second_logical_interface_id,
    )


@router.put("/connections/{connection_id}")
async def put_connection(connection_id, request: Request):
    return utils.update_connection(await request.json())


@router.delete("/connections/{connection_id}")
def delete_connection(connection_id):
    utils.delete_connection(connection_id)
    return "Connection deleted successfully", 200
