from fastapi.routing import APIRouter
from api.schemas.schemas import (
    ConnectionList,
    Device,
    Connection,
    ConnectionBase,
    ConnectionComplete,
)
import api.core.utils as utils
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get("/device", response_model=Device)
def get_device():
    return utils.get_device_information()


@router.delete("/device/reset")
def reset_device():
    utils.reset_device()
    return "Device successfully resetted", 200


@router.get("/connections", response_model=ConnectionList)
def get_connections():
    return utils.get_all_connections()


@router.post("/connections", response_model=ConnectionComplete)
def post_connections(connection: ConnectionBase):
    return utils.create_connection(
        connection.connection_name,
        connection.first_logical_interface_id,
        connection.second_logical_interface_id,
    )


@router.put("/connections/{connection_id}", response_model=Connection)
async def put_connection(connection_id, connection: Connection):
    updated_connection = jsonable_encoder(connection)
    return utils.update_connection(updated_connection)


@router.delete("/connections/{connection_id}")
def delete_connection(connection_id):
    utils.delete_connection(connection_id)
    return "Connection deleted successfully", 200
