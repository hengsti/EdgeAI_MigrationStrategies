"""
loadbalancing protocol module
"""
from loguru import logger

from runnables import HeartbeatProtocol

class Loadbalancer:
    """
    Class to handle load balancing between REACTIVE edge devices.
    """
    @classmethod
    def run(cls, edge_device: object, num_services: int, all_devices: list, timestep: int) -> None:
        """
        Distributes services from the given edge device to partner edge devices 
        based on their available CPU cores and heartbeat status.
        Args:
            cls: The class instance (not used in the method logic).
            edge_device (object): The edge device that is attempting to offload services.
            num_services (int): The number of services to be distributed.
            all_devices (list): A list of all edge devices in the network.
            timestep (int): The current timestep in the simulation or process.
        Returns:
            tuple: A tuple containing:
                - partner_devices (list): A list of partner edge devices that received services.
                - servs (list): A list of services that were assigned to the partner devices.
            If no services are distributed, returns (None, None).
        """
        partner_edge_devices = HeartbeatProtocol.get_online_partner_edge_devices(
            edge_device=edge_device,
            all_devices=all_devices,
            timestep=timestep
        )
        partner_devices = []
        servs = []
        
        if partner_edge_devices:
            for partner in partner_edge_devices:
                max_services = max(0, partner.specifications['cpu_cores'] - partner.specifications["reserved_cpu_cores"])
                heartbeat = HeartbeatProtocol.get_heartbeat(partner, timestep)
                if len(partner.services) < max_services and heartbeat:
                    num = max(0, num_services - max_services)
                    servs = list(edge_device.services[:num])
                    partner_devices.append(partner)

            if partner_devices and servs:
                logger.bind(loadbalancing=True).debug(
                    "Timestep: {} - EdgeDevices {} get Services {} assigned from {}",
                    timestep, partner_devices, servs, edge_device.id
                )
                return partner_devices, servs
        return None, None
