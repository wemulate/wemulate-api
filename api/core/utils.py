from typing import Dict, List, Optional
import wemulate.ext.settings as wemulate_settings
import wemulate.ext.utils as wemulate_utils
from wemulate.core.database.models import (
    ConnectionModel,
    LogicalInterfaceModel,
    DEFAULT_PARAMETERS,
    JITTER,
    BANDWIDTH,
    PACKET_LOSS,
    DELAY,
)
from api.schemas.schemas import (
    Connection,
    ConnectionComplete,
    ConnectionList,
    Device,
    LogicalInterface,
    ManagementInterface,
    Settings,
)


def _get_ip_of_interface(interface_name: str) -> Optional[str]:
    return wemulate_settings.get_interface_ip(interface_name)


def _get_mgmt_interfaces() -> List[ManagementInterface]:
    mgmt_interface_names: List[str] = wemulate_settings.get_mgmt_interfaces()
    mgmt_interfaces: List[ManagementInterface] = []
    for mgmt_interface_name in mgmt_interface_names:
        ip_address = _get_ip_of_interface(mgmt_interface_name)
        mgmt_interfaces.append(
            ManagementInterface(
                **{"ip": ip_address, "physical_name": mgmt_interface_name}
            )
        )
    return mgmt_interfaces


def _get_logical_interfaces() -> List[LogicalInterface]:
    physical_interface_names: List[str] = wemulate_settings.get_non_mgmt_interfaces()
    logical_interfaces: List[LogicalInterface] = []
    for physical_interface_name in physical_interface_names:
        logical_interface: LogicalInterfaceModel = (
            wemulate_utils.get_logical_interface_by_physical_name(
                physical_interface_name
            )
        )
        logical_interfaces.append(
            LogicalInterface(
                **{
                    "interface_id": logical_interface.logical_interface_id,
                    "logical_name": logical_interface.logical_name,
                    "physical_name": physical_interface_name,
                }
            )
        )
    return logical_interfaces


def get_device_information() -> Device:
    return Device(
        **{
            "mgmt_interfaces": _get_mgmt_interfaces(),
            "logical_interfaces": _get_logical_interfaces(),
        }
    )


def create_connection(
    connection_name: str,
    first_logical_interface_id: int,
    second_logical_interface_id: int,
) -> ConnectionComplete:
    wemulate_utils.add_connection(
        connection_name,
        wemulate_utils.get_logical_interface_by_id(
            first_logical_interface_id
        ).logical_name,
        wemulate_utils.get_logical_interface_by_id(
            second_logical_interface_id
        ).logical_name,
    )
    return ConnectionComplete(
        **{
            "connection_id": wemulate_utils.get_connection_by_name(
                connection_name
            ).connection_id,
            "connection_name": connection_name,
            "first_logical_interface_id": first_logical_interface_id,
            "second_logical_interface_id": second_logical_interface_id,
            "incoming": {},
            "outgoing": {},
        }
    )


def _get_parameter(connection: ConnectionModel) -> Dict[str, Settings]:
    parameters: Dict[str, Settings] = {
        "incoming": Settings(),
        "outgoing": Settings(),
    }
    if connection.parameters:
        for parameter in connection.parameters:
            if parameter.direction == "incoming":
                setattr(
                    parameters["incoming"], parameter.parameter_name, parameter.value
                )
            else:
                setattr(
                    parameters["outgoing"], parameter.parameter_name, parameter.value
                )
    return parameters


def get_all_connections() -> ConnectionList:
    connections: List[ConnectionModel] = wemulate_utils.get_connection_list()
    connection_information: ConnectionList = ConnectionList(connections=[])
    for connection in connections:
        complete_connection = ConnectionComplete(
            **{
                "connection_name": connection.connection_name,
                "connection_id": connection.connection_id,
                "first_logical_interface_id": connection.first_logical_interface_id,
                "second_logical_interface_id": connection.second_logical_interface_id,
                **_get_parameter(connection),
            }
        )
        connection_information.connections.append(complete_connection)
    return connection_information


def _reset_connection(connection_name: str) -> None:
    wemulate_utils.reset_connection(connection_name)


def _detect_applied_parameters(parameters: Dict[str, int]) -> Dict[str, int]:
    applied_parameter: Dict = {}
    if parameters[JITTER] != DEFAULT_PARAMETERS[JITTER]:
        applied_parameter[JITTER] = parameters[JITTER]
    if parameters[BANDWIDTH] != DEFAULT_PARAMETERS[BANDWIDTH]:
        applied_parameter[BANDWIDTH] = parameters[BANDWIDTH]
    if parameters[DELAY] != DEFAULT_PARAMETERS[DELAY]:
        applied_parameter[DELAY] = parameters[DELAY]
    if parameters[PACKET_LOSS] != DEFAULT_PARAMETERS[PACKET_LOSS]:
        applied_parameter[PACKET_LOSS] = parameters[PACKET_LOSS]
    return applied_parameter


def _set_parameter(
    connection_name: str, parameters: Dict[str, int], direction: str
) -> None:
    wemulate_utils.set_parameter(connection_name, parameters, direction)


def update_connection(connection: Dict) -> Connection:
    _reset_connection(connection["connection_name"])
    for direction in ["incoming", "outgoing"]:
        parameters_to_apply: Dict[str, int] = _detect_applied_parameters(
            connection[direction]
        )
        _set_parameter(connection["connection_name"], parameters_to_apply, direction)
    return Connection(**connection)


def delete_connection(connection_id: int) -> None:
    wemulate_utils.delete_connection(
        wemulate_utils.get_connection_by_id(connection_id).connection_name
    )
