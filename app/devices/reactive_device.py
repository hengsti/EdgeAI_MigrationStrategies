"""
This module defines the ReactiveDevice class,
which extends the BaseDevice class to include reactive 
methods for the offloading.
"""
import random
from loguru import logger

from devices.base_device import BaseDevice

class ReactiveDevice(BaseDevice):
    """
    The ReactiveDevice class extends the BaseDevice class
    to include reactive methods.
    It provides methods to transfer models and data 
    between edge devices and servers in a simulation environment.
    
    Methods:
        - assign_checkpoint_edge_device_to_server(cls, edge_device, server, all_services, offloading, timestep):
            Assigns the checkpoint from the edge device to the server based on the offloading strategy.
        - assign_checkpoint_server_to_edge_device(cls, server, partner_edge_devices, all_services, offloading, max_services, timestep):
            Assigns the checkpoint from the server to the edge device based on the offloading strategy.
    """
    @classmethod
    def assign_checkpoint_edge_device_to_server(
        cls,
        edge_device: object,
        server: object,
        all_services: list,
        offloading: str,
        timestep: int
    ) -> None:
        """
        Assign the checkpoint from the edge device to the server.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            all_services (list): The list of all services.
            offloading (str): The offloading strategy to use (model or data).
            timestep (int): The current timestep in the simulation.
        """
        if offloading == "model":
            for service in all_services:
                if service.server.id == edge_device.id:
                    super().assign_service_edge_device_to_server(
                        edge_device=edge_device,
                        server=server,
                        service=service,
                        timestep=timestep
                    )
                    logger.bind(offloading=True).debug(
                        "Timestep: {} - Checkpoint of Service {} from Edge Device {} assigned to Server {}",
                        timestep, service.id, edge_device.id, server.id
                    )
            return
        if offloading == "data":
            if len(edge_device.temperature_measurement) > 0:
                super().assign_data_to_server(
                    edge_device=edge_device,
                    server=server,
                    timestep=timestep
                )
                logger.bind(offloading=True).debug(
                    "Timestep: {} - Checkpoint of Temperatures from Edge Device {} assigned to Server {}",
                    timestep, edge_device.id, server.id
                )
                return

    @classmethod
    def assign_checkpoint_server_to_edge_device(
        cls,
        server: object,
        partner_edge_devices: list,
        all_services: list,
        offloading: str,
        max_services: int,
        timestep: int
    ) -> None:
        """
        Assign the checkpoint from the server to the edge device.
        Args:
            server (object): The server object.
            partner_edge_devices (list): The list of partner edge devices.
            all_services (list): The list of all services.
            offloading (str): The offloading strategy to use (model or data).
            max_services (int): The maximum number of services that can be assigned to an edge device.
            timestep (int): The current timestep in the simulation.
        """
        if offloading == "model":
            for service in all_services:
                if service.server.id == server.id:
                    # assign service to partner edge device
                    edge_device = next(
                        (device for device in partner_edge_devices if len(device.services) < max_services),
                        None
                    )
                    if edge_device is None:
                        logger.bind(offloading=True).debug(
                            "Timestep: {} - No suitable partner Edge Device found for Service {}",
                            timestep, service.id
                        )
                        return

                    logger.bind(offloading=True).debug(
                        "Timestep: {} - Partner Edge Device {} choosen for Service {}",
                        timestep, edge_device.id, service.id
                    )
                    super().assign_service_server_to_edge_device(
                        server=server,
                        edge_device=edge_device,
                        service=service,
                        timestep=timestep
                    )
                    logger.bind(offloading=True).debug(
                        "Timestep: {} - Checkpoint of Service {} from Server {} assigned to Edge Device {}",
                        timestep, service.id, server.id, edge_device.id
                    )
            return
        if offloading == "data":
            if len(server.temperature_measurement) > 0:
                # take random partner device
                edge_device = random.choice(partner_edge_devices)
                logger.bind(offloading=True).debug(
                        "Timestep: {} - Partner Edge Device {} choosen for Data",
                        timestep, edge_device.id
                    )
                super().assign_data_to_edge_device(
                    server=server,
                    edge_device=edge_device,
                    timestep=timestep
                )
                logger.bind(offloading=True).debug(
                    "Timestep: {} - Checkpoint of Temperatures from Server {} assigned to Edge Device {}",
                    timestep, server.id, edge_device.id
                )
                return
