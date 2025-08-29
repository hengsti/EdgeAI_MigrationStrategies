"""
hearbeat protocol module
"""
from loguru import logger

class HeartbeatProtocol:
    """
    Class for the heartbeat protocol.
    
    Methods
    -------
    - run(edge_device: object, all_devices: list, max_services: int) -> None
        
        Run the heartbeat protocol.
    """
    @classmethod
    def run(cls, edge_device: object, all_devices: list, max_services: int, timestep: int) -> None:
        """
        Run the heartbeat protocol.

        Args:
            edge_device (object): The edge device.
            all_devices (list): The list of all devices.
            max_services (int): The maximum number of services.

        Returns:
            tuple: A tuple containing:
            - heartbeat (bool): The heartbeat status.
            - partner_edge_devices (list or None): The list of partner edge devices if heartbeat is False, otherwise None.
        """
        heartbeat = cls.get_heartbeat(edge_device, timestep)

        if not heartbeat:
            partner_edge_devices = cls._get_partner_edge_devices(edge_device, all_devices, max_services, timestep)
            return heartbeat, partner_edge_devices

        return heartbeat, None

    @classmethod
    def get_heartbeat(cls, edge_device: object, timestep: int) -> bool:
        """
        Get the heartbeat status of the edge device.
        Args:
            edge_device (object): The edge device.
            timestep (int): The current timestep.
        Returns:
            bool: The heartbeat status.
        """
        state = edge_device.status["state"]
        logger.bind(heartbeat=True).debug(
            "Timestep: {} - EdgeDevice {} - State: {}",
            timestep, edge_device.id, state
        )

        if state != "off":
            return True
        return False

    @classmethod
    def _get_partner_edge_devices(
        cls,
        edge_device: object,
        all_devices: list,
        max_services: int,
        timestep: int
    ) -> list:
        """
        Get the partner edge device of the edge device.
        Args:
            edge_device (object): The edge device.
            all_devices (list): The list of all devices.
            max_services (int): The maximum number of services.
            timestep (int): The current timestep.
        Returns:
            list: The list of partner edge devices.
        """
        partners = edge_device.partner_devices
        available_devices = []

        for device in all_devices:
            if device.id in partners:
                if device.status["state"] != "off" and device.status["active"] and len(device.services) < max_services:
                    logger.bind(heartbeat=True).debug(
                        "Timestep: {} - EdgeDevice {} - Found new Partner device: {} with {} concurrent Services",
                        timestep, edge_device.id, device.id, len(device.services)
                    )
                    available_devices.append(device)

        if available_devices:
            logger.bind(heartbeat=True).debug(
                "Timestep: {} - EdgeDevice {} - Available Partner devices: {}",
                timestep, edge_device.id, [device.id for device in available_devices]
            )
            return available_devices

        logger.bind(heartbeat=True).debug(
            "Timestep: {} - EdgeDevice {} - All Partner devices off",
            timestep, edge_device.id
        )
        return None


    @classmethod
    def get_online_partner_edge_devices(
        cls,
        edge_device: object,
        all_devices: list,
        timestep: int
    ) -> list:
        """
        Get the partner edge device of the edge device.
        Args:
            edge_device (object): The edge device.
            all_devices (list): The list of all devices.
            timestep (int): The current timestep.
        Returns:
            list: The list of partner edge devices.
        """
        partners = edge_device.partner_devices
        available_devices = []

        for device in all_devices:
            if device.id in partners:
                if device.status["state"] == "on" and device.status["active"]:
                    logger.bind(heartbeat=True).debug(
                        "Timestep: {} - EdgeDevice {} - Found new Partner device: {}",
                        timestep, edge_device.id, device.id
                    )
                    available_devices.append(device)

        if available_devices:
            logger.bind(heartbeat=True).debug(
                "Timestep: {} - EdgeDevice {} - Available Partner devices: {}",
                timestep, edge_device.id, [device.id for device in available_devices]
            )
            return available_devices

        logger.bind(heartbeat=True).debug(
            "Timestep: {} - EdgeDevice {} - All Partner devices off",
            timestep, edge_device.id
        )
        return None
