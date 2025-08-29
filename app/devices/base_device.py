"""
This module defines the BaseDevice class, which provides methods to manage the state, power,
and data transfer of edge devices in a simulation environment.
The class includes methods to modify the state of edge devices based on available power,
manage power sources, handle data and service transfers between edge devices and servers,
and log relevant information using the loguru logger.
"""

from loguru import logger
from energy_harvesting import EnergyHarvester, HarvesterBattery

class BaseDevice:
    """
    The BaseDevice class provides methods to manage the state, power,
    and data transfer of edge devices in a simulation environment.

    Methods:
        - modify_state(cls, edge_device: object, timestep: int, min_power_required: float = 5.00) -> None:
            Modify the state of the edge device based on the available power.

        - modify_power(cls, edge_device: object, harvester: EnergyHarvester, timestep: int) -> None:
            Modify the power of the edge device based on the available power.
    """
    @classmethod
    def modify_state(cls, edge_device: object, harvester: EnergyHarvester, timestep: int, min_power_required: float = 5.00) -> None:
        """
        Modify the state of the edge device based on the available power.
        Args:
            edge_device (object): The edge device object.
            harvester (EnergyHarvester): The energy harvester object.
            timestep (int): The current timestep in the simulation.
            min_power_required (float): The minimum power required to keep the edge device active.
        """
        if isinstance(harvester, HarvesterBattery):
            cls._modify_state_with_battery(edge_device, harvester, timestep)
        elif isinstance(harvester, EnergyHarvester):
            cls._modify_state_without_battery(edge_device, timestep, min_power_required)
    
    @classmethod
    def _modify_state_without_battery(cls, edge_device: object, timestep: int, min_power_required: float = 5.00) -> None:
        """
        EdgeDevice - Modify the state of the server based on the available power.
        Args:
            edge_device (object): The edge_device object.
            timestep (int): The current timestep in the simulation.
            min_power_required (float): The minimum power required to keep the edge device active.
        """
        if edge_device.actual_power > min_power_required:
            edge_device.status["state"] = "on"
            edge_device.status["active"] = True
        elif 0.00 < edge_device.actual_power <= min_power_required:
            edge_device.status["state"] = "critical"
            edge_device.status["active"] = True
        else:
            edge_device.status["state"] = "off"
            edge_device.status["active"] = False

        logger.bind(status=True).debug(
            "Timestep: {} - EdgeDevice '{}' is in state '{}' - active = '{}'",
            timestep, edge_device.model_name, edge_device.status["state"], edge_device.status["active"]
        )
    
    @classmethod
    def _modify_state_with_battery(cls, edge_device: object, harvester: HarvesterBattery, timestep: int) -> None:
        """
        Modify the state of the edge device based on the available power and battery state.
        Args:
            edge_device (object): The edge device object.
            harvester (HarvesterBattery): The energy harvester object.
            timestep (int): The current timestep in the simulation.
        """
        if edge_device.actual_power > 0.00:       
            if harvester.get_bsoc(edge_device.id) >= harvester.get_max_capacity() * 0.4:
                edge_device.status["state"] = "on"
                edge_device.status["active"] = True
            elif harvester.get_min_bsoc() <= harvester.get_bsoc(edge_device.id) < harvester.get_max_capacity() * 0.4:
                edge_device.status["state"] = "critical"
                edge_device.status["active"] = True
        else:
            edge_device.status["state"] = "off"
            edge_device.status["active"] = False

        logger.bind(status=True).debug(
            "Timestep: {} - EdgeDevice '{}' is in state '{}' - active = '{}'",
            timestep, edge_device.model_name, edge_device.status["state"], edge_device.status["active"]
        )
        
    @classmethod
    def modify_power(cls, edge_device: object, harvester, timestep: int, required_power: float) -> None:
        """
        Modify the power of the edge device based on the available power.
        Args:
            edge_device (object): The edge device object.
            harvester (EnergyHarvester OR HarvesterBattery): The energy harvester object.
            timestep (int): The current timestep in the simulation.
            required_power (float): The required power for the edge device.
        """
        if isinstance(harvester, HarvesterBattery):
            cls._modify_power_with_battery(edge_device, harvester, timestep, required_power)
        elif isinstance(harvester, EnergyHarvester):
            cls._modify_power_without_battery(edge_device, harvester, timestep)

    @classmethod
    def _modify_power_without_battery(cls, edge_device: object, harvester: EnergyHarvester, timestep: int) -> None:
        """
        Modify the power of the edge device without using a battery.
        Args:
            edge_device (object): The edge device object.
            harvester (EnergyHarvester): The energy harvester object.
            timestep (int): The current timestep in the simulation.
        """
        device_id = edge_device.id
        actual_power, power_source = cls._get_highest_available_power(device_id, harvester, timestep)
        edge_device.actual_power = actual_power
        edge_device.power_source = power_source
        logger.bind(status=True).debug(
            "Timestep: {} - Power at EdgeDevice '{}': '{}' W from source '{}'",
            timestep, device_id, actual_power, power_source
        )

    @classmethod
    def _modify_power_with_battery(cls, edge_device: object, harvester: HarvesterBattery, timestep: int, required_power: float) -> None:
        """
        Modify the power of the edge device using a battery.
        Args:
            edge_device (object): The edge device object.
            harvester (HarvesterBattery): The energy harvester object.
            timestep (int): The current timestep in the simulation.
            required_power (float): The required power for the edge device.
        """
        device_id = edge_device.id
        harvester.charge_battery(device_id=device_id, timestep=timestep)
        success = harvester.consume_energy(device_id=device_id, required_power_w=required_power, timestep=timestep)
        edge_device.actual_power = required_power if success else 0.00
        edge_device.power_source = "battery"
        logger.bind(status=True).debug(
            "Timestep: {} - Power at EdgeDevice '{}': '{}' W from battery (success: {})",
            timestep, device_id, edge_device.actual_power, success
        )


    @classmethod
    def _get_highest_available_power(cls, device_id: int, harvester: EnergyHarvester, timestep: int) -> tuple:
        """
        Get the available solar and wind power at the current time index.
        Args:
            device_id (int): The ID of the edge device.
            harvester (EnergyHarvester): The energy harvester object.
            timestep (int): The current timestep in the simulation.
        Returns:
            tuple: A tuple containing:
            - actual_power (float): The actual power available at the edge device.
            - power_source (str): The power source (solar, wind, or none) with the highest power.
        """
        available_power = harvester.get_energy(device_id=device_id)
        if available_power["solar"] > available_power["wind"]:
            actual_power = available_power["solar"]
            power_source = "solar"
        else:
            actual_power = available_power["wind"]
            power_source = "wind"

        if actual_power == 0.00:
            power_source = "none"

        logger.bind(status=True).debug(
            "Timestep: {} - Available power at EdgeDevice '{}': '{}' Watt from source '{}'",
            timestep, device_id, actual_power, power_source
        )

        return actual_power, power_source

    @classmethod
    def update_transfer_duration(cls, device: object, timestep: int):
        """
        Increment transfer duration and check if transfer is complete.
        Args:
            device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        Returns:
            bool: True if the transfer duration is completed, False otherwise.
        """
        device.transfer_model["transfer_duration"] += 1
        if device.transfer_model["transfer_duration"] >= device.transfer_model["transfer_time"]:
            logger.bind(offloading=True).debug(
                "Timestep: {} - Transfer duration for EdgeDevice '{}' completed",
                timestep, device.id
            )
            return True

        logger.bind(offloading=True).debug(
            "Timestep: {} - Transfer duration for EdgeDevice '{}': {}",
            timestep, device.id, device.transfer_model["transfer_duration"]
        )
        return False

    @classmethod
    def reset_transfer_state(cls, device: object, timestep: int):
        """
        Reset the transfer state of a device.
        Args:
            device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        """
        device.transfer_model["transfer"] = False
        device.transfer_model["transfer_duration"] = 0
        logger.bind(offloading=True).debug(
            "Timestep: {} - Transfer state reset for EdgeDevice '{}' - transfer: {}, duration: {}",
            timestep, device.id, device.transfer_model["transfer"], device.transfer_model["transfer_duration"]
        )

    @classmethod
    def start_transfer(cls, device: object, timestep: int):
        """
        Initiate a new transfer.
        Args:
            device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        """
        device.transfer_model["transfer"] = True
        device.transfer_model["transfer_duration"] = 0
        logger.bind(offloading=True).debug(
            "Timestep: {} - Transfer initiated for EdgeDevice '{}' - transfer: {}, duration: {}",
            timestep, device.id, device.transfer_model["transfer"], device.transfer_model["transfer_duration"]
        )

    @classmethod
    def assign_transfer_id_to_edge_device(cls, edge_device: object, server: object, timestep: int):
        """
        Assign device IDs for the transfer from a server to an edge device.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
        """
        edge_device.transfer_model["transfer_from_device_id"] = server.id
        logger.bind(offloading=True).debug(
            "Timestep: {} - Transfer ID assigned for EdgeDevice '{}' - transfer_from_device_id: {}",
            timestep, edge_device.id, edge_device.transfer_model["transfer_from_device_id"]
        )

    @classmethod
    def assign_transfer_id_to_server(cls, server: object, edge_device: object, timestep: int):
        """
        Assign device IDs for the transfer from an edge device to a server.
        Args:
            server (object): The server object.
            edge_device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        """
        edge_device.transfer_model["transfer_to_device_id"] = server.id
        logger.bind(offloading=True).debug(
            "Timestep: {} - Transfer ID assigned for EdgeDevice '{}' - transfer_to_device_id: {}",
            timestep, edge_device.id, edge_device.transfer_model["transfer_to_device_id"]
        )

    @classmethod
    def reset_transfer_id_to_server(cls, edge_device: object, timestep: int):
        """
        Reset device IDs after transfer completion.
        Args:
            edge_device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        """
        edge_device.transfer_model["transfer_to_device_id"] = 0
        logger.bind(offloading=True).debug(
            "Timestep: {} - Transfer ID reset for EdgeDevice '{}' - transfer_to_device_id: {}",
            timestep, edge_device.id, edge_device.transfer_model["transfer_to_device_id"]
        )

    @classmethod
    def reset_transfer_id_to_edge_device(cls, edge_device: object, timestep: int):
        """
        Reset device IDs after transfer completion.
        Args:
            edge_device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        """
        edge_device.transfer_model["transfer_from_device_id"] = 0
        logger.bind(offloading=True).debug(
            "Timestep: {} - Transfer ID reset for EdgeDevice '{}' - transfer_from_device_id: {}",
            timestep, edge_device.id, edge_device.transfer_model["transfer_from_device_id"]
        )

    @classmethod
    def transfer_failed(cls, edge_device: object, timestep: int) -> bool:
        """
        Check if a transfer failed due to low power availability
        Args:
            edge_device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        Returns:
            bool: True if the transfer failed, False otherwise.
        """
        if edge_device.transfer_model["transfer_duration"] >= edge_device.transfer_model["transfer_time"]:
            logger.bind(offloading=True).debug(
                "Timestep: {} - Transfer of Model from EdgeDevice '{}' already completed (duration: {})",
                timestep, edge_device.id, edge_device.transfer_model["transfer_duration"]
            )
            return False

        if edge_device.actual_power == 0.00:
            logger.bind(offloading=True).debug(
                "Timestep: {} - Transfer of Model from EdgeDevice '{}' failed due to low power (duration: {})",
                timestep, edge_device.id, edge_device.transfer_model["transfer_duration"]
            )
            return True

        return False

    @classmethod
    def assign_service_edge_device_to_server(
        cls,
        edge_device: object,
        server: object,
        service: object,
        timestep: int
    ):
        """
        Assign the service from the edge device to the server.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            service (object): The service object.
            timestep (int): The current timestep in the simulation.
        """
        if service in edge_device.services:
            edge_device.services.remove(service)
            server.services.append(service)
            service.server = server
            logger.bind(offloading=True).debug(
                "Timestep: {} - Service {} assigned from EdgeDevice '{}' to Server '{}'",
                timestep, service.id, edge_device.id, server.id
            )
        else:
            logger.bind(offloading=True).debug(
                "Timestep: {} - Service {} not found in EdgeDevice '{}'",
                timestep, service.id, edge_device.id
            )

    @classmethod
    def assign_service_server_to_edge_device(
        cls,
        server: object,
        edge_device: object,
        service: object,
        timestep: int
    ):
        """
        Assign the service from the server to the edge device.
        Args:
            server (object): The server object.
            edge_device (object): The edge device object.
            service (object): The service object.
            timestep (int): The current timestep in the simulation.
        """
        if service in server.services:
            server.services.remove(service)
            edge_device.services.append(service)
            service.server = edge_device
            logger.bind(offloading=True).debug(
                "Timestep: {} - Service {} assigned from Server '{}' to EdgeDevice '{}'",
                timestep, service.id, server.id, edge_device.id
            )
        else:
            logger.bind(offloading=True).debug(
                "Timestep: {} - Service {} not found in Server '{}'",
                timestep, service.id, server.id
            )

    @classmethod
    def assign_data_to_server(
        cls,
        edge_device: object,
        server: object,
        timestep: int
    ):
        """
        Assign the data from the edge device to the server.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
        """
        server.temperature_measurement.extend(edge_device.temperature_measurement)
        edge_device.temperature_measurement.clear()

        logger.bind(offloading=True).debug(
            "Timestep: {} - Data assigned from EdgeDevice '{}' to Server '{}'",
            timestep, edge_device.id, server.id
        )

    @classmethod
    def assign_data_to_edge_device(
        cls,
        server: object,
        edge_device: object,
        timestep: int
    ):
        """
        Assign the data from the server to the edge device.
        Args:
            server (object): The server object.
            edge_device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        """
        edge_device.temperature_measurement.extend(server.temperature_measurement)
        server.temperature_measurement.clear()

        logger.bind(offloading=True).debug(
            "Timestep: {} - Data assigned from Server '{}' to EdgeDevice '{}'",
            timestep, server.id, edge_device.id
        )
