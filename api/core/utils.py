from typing import Dict, List
from sqlalchemy.sql.sqltypes import Boolean
import wemulate
import wemulate.ext.settings as wemulate_settings
import wemulate.ext.utils as wemulate_utils
from wemulate.core.database.models import ConnectionModel, LogicalInterfaceModel

STANDARD_DELAY = 0
STANDARD_BANDWIDTH = 1000
STANDARD_PACKET_LOSS = 0
STANDARD_JITTER = 0


def _get_ip_of_interface(interface_name: str) -> str:
    return wemulate_settings.get_interface_ip(interface_name)


def get_mgmt_interfaces() -> List[Dict]:
    mgmt_interface_names: List[str] = wemulate_settings.get_mgmt_interfaces()
    mgmt_interfaces: List[Dict] = []
    for mgmt_interface_name in mgmt_interface_names:
        ip_address = _get_ip_of_interface(mgmt_interface_name)
        mgmt_interfaces.append({"ip": ip_address, "physical_name": mgmt_interface_name})
    return mgmt_interfaces


def get_logical_interfaces() -> List[Dict]:
    physical_interface_names: List[str] = wemulate_settings.get_interfaces()
    logical_interfaces: List[Dict] = []
    for physical_interface_name in physical_interface_names:
        logical_interface: LogicalInterfaceModel = (
            wemulate_utils.get_logical_interface_by_physical_name(
                physical_interface_name
            )
        )
        logical_interfaces.append(
            {
                "interface_id": logical_interface.logical_interface_id,
                "logical_name": logical_interface.logical_name,
                "physical_name": physical_interface_name,
            }
        )
    return logical_interfaces


def create_connection(
    connection_name: str,
    first_logical_interface_id: int,
    second_logical_interface_id: int,
):
    wemulate_utils.add_connection(
        connection_name,
        wemulate_utils.get_logical_interface_by_id(
            first_logical_interface_id
        ).logical_name,
        wemulate_utils.get_logical_interface_by_id(
            second_logical_interface_id
        ).logical_name,
    )
    return {
        "connection_id": wemulate_utils.get_connection_by_name(
            connection_name
        ).connection_id,
        "connection_name": connection_name,
        "first_logical_interface_id": first_logical_interface_id,
        "second_logical_interface_id": second_logical_interface_id,
        **_get_standard_parameter_values(),
    }


def _get_standard_parameter_values() -> Dict:
    return {
        "delay": STANDARD_DELAY,
        "packet_loss": STANDARD_PACKET_LOSS,
        "bandwidth": STANDARD_BANDWIDTH,
        "jitter": STANDARD_JITTER,
    }


def _get_parameter(connection: ConnectionModel) -> Dict:
    parameters: Dict = _get_standard_parameter_values()
    if connection.parameters:
        for parameter in connection.parameters:
            parameters[parameter.parameter_name] = parameter.value
    return parameters


def get_all_connections() -> List[Dict]:
    connections: List[ConnectionModel] = wemulate_utils.get_connection_list()
    connection_information: List[Dict] = []
    for connection in connections:
        connection_information.append(
            {
                "connection_name": connection.connection_name,
                "connection_id": connection.connection_id,
                "first_logical_interface_id": connection.first_logical_interface_id,
                "second_logical_interface_id": connection.second_logical_interface_id,
                **_get_parameter(connection),
            }
        )
    return connection_information


def _reset_connection(connection_name: str) -> None:
    wemulate_utils.reset_connection(connection_name)


def _detect_applied_parameters(parameter: Dict) -> Dict:
    applied_parameter: Dict = {}
    if parameter["jitter"] != STANDARD_JITTER:
        applied_parameter["jitter"] = parameter["jitter"]
    if parameter["bandwidth"] != STANDARD_BANDWIDTH:
        applied_parameter["bandwidth"] = parameter["bandwidth"]
    if parameter["delay"] != STANDARD_DELAY:
        applied_parameter["delay"] = parameter["delay"]
    if parameter["packet_loss"] != STANDARD_PACKET_LOSS:
        applied_parameter["packet_loss"] = parameter["packet_loss"]
    return applied_parameter


def _set_parameter(connection_name: str, parameter: Dict) -> None:
    wemulate_utils.set_parameter(connection_name, parameter)


def update_connection(parameter: Dict) -> Dict:
    parameter_to_apply: Dict[str, int] = _detect_applied_parameters(parameter)
    if not parameter_to_apply:
        _reset_connection(parameter["connection_name"])
    else:
        _set_parameter(parameter["connection_name"], parameter_to_apply)
    return parameter


def delete_connection(connection_id: int) -> None:
    wemulate_utils.delete_connection(
        wemulate_utils.get_connection_by_id(connection_id).connection_name
    )
