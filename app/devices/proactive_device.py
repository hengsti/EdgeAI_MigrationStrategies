"""
This module defines the ProactiveDevice class,
which extends the BaseDevice class to include proactive 
methods for the offloading.
"""
from loguru import logger

from energy_harvesting import EnergyHarvester, HarvesterBattery
from devices.base_device import BaseDevice

class ProactiveDevice(BaseDevice):
    """
    The ProactiveDevice class extends the BaseDevice class
    to include proactive methods for managing model and data transfers
    between edge devices and servers in a simulation environment.

    Key Methods:
        - transfer_to_server:
            Handles the proactive transfer of models or data from an edge device to a server.

        - transfer_to_edge_device:
            Handles the proactive transfer of models or data from the server to edge devices.
    """
    @classmethod
    def _get_low_power(
        cls,
        edge_device: object,
        min_power_required: float,
        timestep: int
    ) -> bool:
        """
        Get the power (0.00 - `min_power_required` Watt) for the edge_device.
        Args:
            edge_device (object): The edge device object.
            harvester (EnergyHarvester): The energy harvester object.
            min_power_required (float): The minimum power required to initiate a transfer.
            timestep (int): The current timestep in the simulation.
        Returns:
            bool: True if the power is less than `min_power_required`, False otherwise.
        """
        if edge_device.actual_power >= min_power_required:
            logger.bind(status=True).debug(
                "Timestep: {} - EdgeDevice '{}' has sufficient current power ({} W) — no need to initiate transfer.",
                timestep, edge_device.id, edge_device.actual_power
            )
            return False
        return True

    @classmethod
    def _get_low_battery_power(
        cls,
        edge_device: object,
        min_power_required: float,
        harvester: EnergyHarvester,
        timestep: int
    ):
        """
        Get the battery power (< `min_power_required` Watt) for the device.
        Args:
            edge_device (object): The edge device object.
            harvester (EnergyHarvester): The energy harvester object.
            min_power_required (float): The minimum power required to initiate a transfer.
            timestep (int): The current timestep in the simulation.
        Returns:
            bool: True if the battery power is less than `min_power_required`, False otherwise.
        """
        bsoc = harvester.get_bsoc(device_id=edge_device.id)     # in Wh
        min_power_required_wh = round(min_power_required * (1 / 3600.0), 2)     # Convert W to Wh
        
        if bsoc >= min_power_required_wh and bsoc > harvester.get_max_capacity() * 0.4:
            # Check if the battery state of charge is above the minimum threshold
            # and if the current power is sufficient
            logger.bind(status=True).debug(
                "Timestep: {} - EdgeDevice '{}' has sufficient battery power ({} Wh) — no need to initiate transfer.",
                timestep, edge_device.id, bsoc
            )
            return False

        logger.bind(status=True).debug(
            "Timestep: {} - EdgeDevice '{}' has no sufficient battery power ({} Wh) — need to initiate transfer.",
            timestep, edge_device.id, bsoc
        )
        return True

    @classmethod
    def _get_high_power(
        cls,
        edge_device: object,
        min_power_required: float,
        timestep: int
    ) -> bool:
        """
        Get the high power (> `min_power_required` Watt) forecast for the device.
        Args:
            edge_device (object): The edge device object.
            harvester (EnergyHarvester): The energy harvester object.
            min_power_required (float): The minimum power required to initiate a transfer.
            timestep (int): The current timestep in the simulation.
        Returns:
            bool: True if the power is greater than `min_power_required`, False otherwise.
        """
        if edge_device.actual_power >= min_power_required:
            logger.bind(status=True).debug(
                "Timestep: {} - EdgeDevice '{}' has high power forecast in the next timestep",
                timestep, edge_device.id
            )
            return True

        logger.bind(status=True).debug(
            "Timestep: {} - EdgeDevice '{}' has no high power forecast in the next timestep",
            timestep, edge_device.id
        )
        return False
    
    @classmethod
    def _get_high_battery_power(
        cls,
        edge_device: object,
        harvester: EnergyHarvester,
        min_power_required: float,
        timestep: int
    ):
        """
        Get the battery power (> `min_power_required` Watt) for the device.
        Args:
            edge_device (object): The edge device object.
            harvester (EnergyHarvester): The energy harvester object.
            min_power_required (float): The minimum power required to initiate a transfer.
            timestep (int): The current timestep in the simulation.

        Returns:
            bool: True if the battery power is greater than `min_power_required`, False otherwise.
        """
        bsoc = harvester.get_bsoc(device_id=edge_device.id)
        min_power_required_wh = min_power_required * (1 / 3600.0)     # Convert W to Wh

        if bsoc >= min_power_required_wh and bsoc > harvester.get_max_capacity() * 0.4:
            # Check if the battery state of charge is above the minimum threshold
            # and if the current power is sufficient
            logger.bind(status=True).debug(
                "Timestep: {} - EdgeDevice '{}' has sufficient battery power ({} Wh)",
                timestep, edge_device.id, bsoc
            )
            return True
        logger.bind(status=True).debug(
            "Timestep: {} - EdgeDevice '{}' has no sufficient battery power ({} Wh)",
            timestep, edge_device.id, bsoc
        )
        return False
        

    @classmethod
    def _transfer_model_to_server(
        cls,
        edge_device: object,
        server: object,
        timestep: int,
        min_power_required: float,
        harvester: object
    ) -> bool:
        """
        Initiate the transfer of the model from the edge device to the server.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
            min_power_required (float): The minimum power required to initiate a transfer.
            harvester (object): The energy harvester object.

        Returns:
            bool: True if the transfer is initiated, False otherwise.
        """
        if edge_device.transfer_model["transfer"]:
            return False

        if isinstance(harvester, HarvesterBattery):
            transfer_initiate = cls._get_low_battery_power(edge_device, min_power_required, harvester, timestep)
        else:
            transfer_initiate = cls._get_low_power(edge_device, min_power_required, timestep)

        if transfer_initiate:
            services_to_transfer = [service.id for service in edge_device.services]
            edge_device.transfer_model["transfer_service_ids"] = services_to_transfer
            super().start_transfer(device=edge_device, timestep=timestep)
            super().assign_transfer_id_to_server(edge_device=edge_device, server=server, timestep=timestep)
            logger.bind(offloading=True).debug(
                "Timestep: {} - UPLOAD initiated - EdgeDevice '{}' uploading Services {} to Server '{}' - Duration: {}",
                timestep, edge_device.id, services_to_transfer, server.id, edge_device.transfer_model["transfer_duration"]
            )
            return False

        return False
    
    @classmethod
    def _update_ongoing_transfers_to_server(cls, edge_device: object, server: object, timestep: int):
        """
        Update and maintain the ongoing model transfers to the server.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
        """
        if super().transfer_failed(edge_device=edge_device, timestep=timestep):
            super().reset_transfer_state(device=edge_device, timestep=timestep)
            super().reset_transfer_id_to_server(edge_device=edge_device, timestep=timestep)
            edge_device.transfer_model["transfer_service_ids"] = []
            edge_device.transfer_model["transfer_failed"] += 1
        elif super().update_transfer_duration(device=edge_device, timestep=timestep):
            service_ids = edge_device.transfer_model.get("transfer_service_ids", [])
            services_to_assign = [s for s in edge_device.services if s.id in service_ids]

            for service in services_to_assign:
                super().assign_service_edge_device_to_server(
                    edge_device=edge_device,
                    server=server,
                    service=service,
                    timestep=timestep
                )
                logger.bind(offloading=True).debug(
                    "Timestep: {} - UPLOAD completed - Service '{}' moved from EdgeDevice '{}' to Server '{}'",
                    timestep, service.id, edge_device.id, server.id
                )

            edge_device.services = [s for s in edge_device.services if s.id not in service_ids]
            super().reset_transfer_state(device=edge_device, timestep=timestep)
            super().reset_transfer_id_to_server(edge_device=edge_device, timestep=timestep)
            edge_device.transfer_model["transfer_service_ids"] = []
            edge_device.transfer_model["transfer_succeded"] += 1
    
    @classmethod
    def _update_ongoing_transfers_model(cls, all_edge_devices: list, server: object, timestep: int):
        """
        Update the ongoing transfers to the server.
        Args:
            all_edge_devices (list): The list of all edge devices.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
        """
        for edge_device in all_edge_devices:
            if edge_device.transfer_model["transfer"] and edge_device.transfer_model["transfer_to_device_id"] != 0:
                cls._update_ongoing_transfers_to_server(edge_device=edge_device, server=server, timestep=timestep)
            if edge_device.transfer_model["transfer"] and edge_device.transfer_model["transfer_from_device_id"] != 0:
                cls._update_ongoing_transfers_to_device(edge_device=edge_device, server=server, timestep=timestep)

    @classmethod
    def _transfer_model_to_edge_device(
        cls,
        server: object,
        edge_device: object,
        harvester: object,
        services: list,
        timestep: int,
        min_power_required: float
    ) -> bool:
        """
        Initiate the transfer of the model from the server to the edge device.
        Args:
            server (object): The server object.
            edge_device (object): The edge device object.
            harvester (object): The energy harvester object.
            services (list): The list of services to be transferred.
            timestep (int): The current timestep in the simulation.
            min_power_required (float): The minimum power required to initiate a transfer.

        Returns:
            bool: True if the transfer is initiated, False otherwise.
        """
        if edge_device.transfer_model["transfer"]:
            return False

        if isinstance(harvester, HarvesterBattery):
            transfer_initiate = cls._get_high_battery_power(edge_device, harvester, min_power_required, timestep)
        else:
            transfer_initiate = cls._get_high_power(edge_device, min_power_required, timestep)

        if transfer_initiate:
            edge_device.transfer_model["transfer_service_ids"] = [s.id for s in services]
            super().start_transfer(device=edge_device, timestep=timestep)
            super().assign_transfer_id_to_edge_device(edge_device=edge_device, server=server, timestep=timestep)
            logger.bind(offloading=True).debug(
                "Timestep: {} - DOWNLOAD initiated - Server '{}' sending Services {} to EdgeDevice '{}'",
                timestep, server.id, [s.id for s in services], edge_device.id
            )
            return False

        return False
    
    @classmethod
    def _update_ongoing_transfers_to_device(cls, edge_device: object, server: object, timestep: int):
        """
        Update and maintain the ongoing model transfers to the edge device.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
        """
        if super().transfer_failed(edge_device=edge_device, timestep=timestep):
            super().reset_transfer_state(device=edge_device, timestep=timestep)
            super().reset_transfer_id_to_edge_device(edge_device=edge_device, timestep=timestep)
            edge_device.transfer_model["transfer_service_ids"] = []
            server.transfer_model["transfer_failed"] += 1
        elif super().update_transfer_duration(device=edge_device, timestep=timestep):
            service_ids = edge_device.transfer_model.get("transfer_service_ids", [])
            services_to_assign = [s for s in server.services if s.id in service_ids]

            for service in services_to_assign:
                super().assign_service_server_to_edge_device(
                    server=server,
                    edge_device=edge_device,
                    service=service,
                    timestep=timestep
                )
                logger.bind(offloading=True).debug(
                    "Timestep: {} - DOWNLOAD completed - Service '{}' moved from Server '{}' to EdgeDevice '{}'",
                    timestep, service.id, server.id, edge_device.id
                )

            server.services = [s for s in server.services if s.id not in service_ids]
            super().reset_transfer_state(device=edge_device, timestep=timestep)
            super().reset_transfer_id_to_edge_device(edge_device=edge_device, timestep=timestep)
            edge_device.transfer_model["transfer_service_ids"] = []
            server.transfer_model["transfer_succeded"] += 1

    @classmethod
    def _transfer_data_to_server(
        cls,
        edge_device: object,
        server: object,
        harvester: EnergyHarvester,
        timestep: int,
        min_power_required: float
    ) -> bool:
        """
        Initiate the transfer of data from the edge device to the server.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            harvester (EnergyHarvester): The energy harvester object.
            timestep (int): The current timestep in the simulation.
            min_power_required (float): The minimum power required to initiate a transfer.

        Returns:
            bool: True if the transfer is initiated, False otherwise.
        """
        if edge_device.transfer_model["transfer"]:
            return False

        if isinstance(harvester, HarvesterBattery):
            transfer_initiate = cls._get_low_battery_power(edge_device, min_power_required, harvester, timestep)
        else:
            transfer_initiate = cls._get_low_power(edge_device, min_power_required, timestep)

        if transfer_initiate:
            super().start_transfer(device=edge_device, timestep=timestep)
            super().assign_transfer_id_to_server(edge_device=edge_device, server=server, timestep=timestep)
            logger.bind(offloading=True).debug(
                "Timestep: {} - UPLOAD initiated - EdgeDevice '{}' uploading Data to Server '{}' - Duration: {}",
                timestep, edge_device.id, server.id, edge_device.transfer_model["transfer_duration"]
            )
            return False

        return False

    @classmethod
    def _transfer_data_to_edge_device(
        cls,
        server: object,
        edge_device: object,
        harvester: EnergyHarvester,
        timestep: int,
        min_power_required: float
    ) -> bool:
        """
        Initiate the transfer of data from the server to the edge device.
        Args:
            server (object): The server object.
            edge_device (object): The edge device object.
            harvester (EnergyHarvester): The energy harvester object.
            timestep (int): The current timestep in the simulation.
            min_power_required (float): The minimum power required to initiate a transfer.

        Returns:
            bool: True if the transfer is initiated, False otherwise.
        """
        if edge_device.transfer_model["transfer"]:
            return False

        if isinstance(harvester, HarvesterBattery):
            transfer_initiate = cls._get_low_battery_power(edge_device, min_power_required, harvester, timestep)
        else:
            transfer_initiate = cls._get_low_power(edge_device, min_power_required, timestep)

        if transfer_initiate:
            super().start_transfer(device=edge_device, timestep=timestep)
            super().assign_transfer_id_to_edge_device(edge_device=edge_device, server=server, timestep=timestep)
            logger.bind(offloading=True).debug(
                "Timestep: {} - DOWNLOAD initiated - Server '{}' sending Data to EdgeDevice '{}' - Duration: {}",
                timestep, server.id, edge_device.id, edge_device.transfer_model["transfer_duration"]
            )
            return False

        return False
    
    @classmethod
    def _update_ongoing_transfers_data(cls, all_edge_devices: list, server: object, timestep: int):
        """
        Update the ongoing transfers to the server.
        Args:
            all_edge_devices (list): The list of all edge devices.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
        """
        for edge_device in all_edge_devices:
            if edge_device.transfer_model["transfer"] and edge_device.transfer_model["transfer_to_device_id"] != 0:
                cls._update_ongoing_data_transfer_to_server(edge_device=edge_device, server=server, timestep=timestep)
            if edge_device.transfer_model["transfer"] and edge_device.transfer_model["transfer_from_device_id"] != 0:
                cls._update_ongoing_data_transfer_to_edge_device(edge_device=edge_device, server=server, timestep=timestep)
    
    @classmethod
    def update_ongoing_transfers(cls, offloading: str, all_devices: list, server: object, timestep: int):
        """
        Update the ongoing transfers based on the offloading strategy.
        Args:
            offloading (str): The offloading strategy to use (model or data).
            all_devices (list): The list of all edge devices.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
        """
        if offloading == "model":
            cls._update_ongoing_transfers_model(
                all_edge_devices=all_devices,
                server=server,
                timestep=timestep
            )
        elif offloading == "data":
            cls._update_ongoing_transfers_data(
                all_edge_devices=all_devices,
                server=server,
                timestep=timestep
            )
    
    @classmethod
    def _update_ongoing_data_transfer_to_server(cls, edge_device: object, server: object, timestep: int):
        """
        Update and maintain the ongoing data transfers to the server.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
        """
        if super().transfer_failed(edge_device=edge_device, timestep=timestep):
            super().reset_transfer_state(device=edge_device, timestep=timestep)
            super().reset_transfer_id_to_server(edge_device=edge_device, timestep=timestep)
            edge_device.transfer_model["transfer_failed"] += 1
        elif super().update_transfer_duration(device=edge_device, timestep=timestep):
            super().assign_data_to_server(edge_device=edge_device, server=server, timestep=timestep)
            logger.bind(offloading=True).debug(
                "Timestep: {} - UPLOAD completed - Data moved from EdgeDevice '{}' to Server '{}'",
                timestep, edge_device.id, server.id
            )
            super().reset_transfer_state(device=edge_device, timestep=timestep)
            super().reset_transfer_id_to_server(edge_device=edge_device, timestep=timestep)
            edge_device.transfer_model["transfer_succeded"] += 1

    @classmethod
    def _update_ongoing_data_transfer_to_edge_device(cls, server: object, edge_device: object, timestep: int):
        """
        Update and maintain the ongoing data transfers to the edge device.
        Args:
            server (object): The server object.
            edge_device (object): The edge device object.
            timestep (int): The current timestep in the simulation.
        """
        if super().transfer_failed(edge_device=edge_device, timestep=timestep):
            super().reset_transfer_state(device=edge_device, timestep=timestep)
            super().reset_transfer_id_to_edge_device(edge_device=edge_device, timestep=timestep)
            server.transfer_model["transfer_failed"] += 1
        elif super().update_transfer_duration(device=edge_device, timestep=timestep):
            super().assign_data_to_edge_device(server=server, edge_device=edge_device, timestep=timestep)
            logger.bind(offloading=True).debug(
                "Timestep: {} - DOWNLOAD completed - Data moved from Server '{}' to EdgeDevice '{}'",
                timestep, server.id, edge_device.id
            )
            super().reset_transfer_state(device=edge_device, timestep=timestep)
            super().reset_transfer_id_to_edge_device(edge_device=edge_device, timestep=timestep)
            server.transfer_model["transfer_succeded"] += 1

    @classmethod
    def transfer_to_server(
        cls,
        edge_device: object,
        server: object,
        timestep: int,
        min_power_required: float,
        offloading: str,
        harvester: EnergyHarvester
    ) -> bool:
        """
        Transfer the model/data to the server.
        Args:
            edge_device (object): The edge device object.
            server (object): The server object.
            timestep (int): The current timestep in the simulation.
            min_power_required (float): The minimum power required to initiate a transfer.
            offloading (str): The offloading strategy to use (model or data).
            harvester (EnergyHarvester): The energy harvester object.
        Returns:
            bool: True if the transfer is initiated, False otherwise.
        """
        if offloading == "model":
            logger.bind(offloading=True).debug(
                "Timestep: {} - Checking transfer to Server {}",
                timestep, edge_device.id
            )
            return cls._transfer_model_to_server(
                edge_device=edge_device,
                server=server,
                timestep=timestep,
                min_power_required=min_power_required,
                harvester=harvester
            )
        elif offloading == "data":
            if len(edge_device.temperature_measurement) > 0:
                logger.bind(offloading=True).debug(
                    "Timestep: {} - Checking transfer to Server {} for Data",
                    timestep, edge_device.id
                )
                return cls._transfer_data_to_server(
                    edge_device=edge_device,
                    server=server,
                    harvester=harvester,
                    timestep=timestep,
                    min_power_required=min_power_required
                )

    @classmethod
    def transfer_to_edge_device(
        cls,
        server: object,
        all_edge_devices: list,
        harvester: EnergyHarvester,
        all_services: object,
        timestep: int,
        min_power_required: float,
        offloading: str,
        loadbalancing: bool
    ) -> bool:
        """
        Transfer the model/data to the edge device.
        Args:
            server (object): The server object.
            all_edge_devices (list): The list of all edge devices.
            harvester (EnergyHarvester): The energy harvester object.
            all_services (object): The list of all services.
            timestep (int): The current timestep in the simulation.
            min_power_required (float): The minimum power required to initiate a transfer.
            offloading (str): The offloading strategy to use (model or data).
            loadbalancing (bool): Whether to use load balancing or not.
        Returns:
            tuple: A tuple containing a boolean indicating if the transfer is completed and the ID of the edge device.
        """
        results = []

        if offloading == "model":
            services_to_transfer = [s for s in all_services if s.server.id == server.id]
            
            transferring_service_ids = set()
            for device in all_edge_devices:
                transferring_service_ids.update(device.transfer_model.get("transfer_service_ids", []))

            for edge_device in all_edge_devices:
                if edge_device.model_type != "edge_device" or edge_device.status["state"] != "on":
                    continue
                
                free_slots = 1
                if loadbalancing:
                    device_slots = edge_device.specifications['cpu_cores'] - edge_device.specifications['reserved_cpu_cores'] - len(edge_device.services)
                    free_slots = max(0, device_slots)
                    if free_slots <= 0:
                        continue
                else:
                    if edge_device.services:
                        continue

                # assignable_services = services_to_transfer[:free_slots]
                # if not assignable_services:
                #     continue
                
                assignable_services = [s for s in services_to_transfer if s.id not in transferring_service_ids][:free_slots]
                if not assignable_services:
                    continue

                transfer_result = cls._transfer_model_to_edge_device(
                    server=server,
                    edge_device=edge_device,
                    harvester=harvester,
                    services=assignable_services,
                    timestep=timestep,
                    min_power_required=min_power_required
                )
                if transfer_result:
                    for service in assignable_services:
                        services_to_transfer.remove(service)
                    results.append({"success": True, "edge_device_id": edge_device.id})

            return results
        if offloading == "data":
            if len(server.temperature_measurement) > 0:
                for edge_device in all_edge_devices:
                    if (
                        edge_device.model_type == "edge_device"
                        and edge_device.status["state"] == "on"
                        and len(edge_device.temperature_measurement) == 0
                    ):
                        logger.bind(offloading=True).debug(
                            "Timestep: {} - Checking transfer to Edge Device {} for Data",
                            timestep, edge_device.id
                        )
                        transfer_result = cls._transfer_data_to_edge_device(
                                server=server,
                                edge_device=edge_device,
                                harvester=harvester,
                                timestep=timestep,
                                min_power_required=min_power_required
                        )
                        if transfer_result:
                            results.append({"success": True, "edge_device_id": edge_device.id})
            return results
