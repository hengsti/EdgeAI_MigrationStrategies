"""
Simulation module for the proactive strategy.
"""
from loguru import logger

from edge_sim_py import Service, EdgeServer

from runnables import AIModel, Measurement
from devices import ProactiveDevice as Device
from utils import custom_collect_service, custom_collect_edge_server_proactive

from simulations.simulation_base import SimulationBase

class SimulationProactive(SimulationBase):
    """
    Simulation class for the proactive strategy.
    """
    def __init__(self, config_variables):
        """
        Initializes the simulation with the configuration variables.
        """
        super().__init__(config_variables=config_variables)

        self.min_power_threshold = round(config_variables["proactive"]["min_power_threshold"], 2)

    def update_simulation(self, parameters: dict) -> None:
        """
        Updates the simulation state for each timestep
        by processing edge devices and centralized servers.
        """
        current_timestep = parameters["current_step"]
        if parameters["current_step"] % 100 == 0:
            logger.bind(simulation=True).info("Progress - Timestep: {}/{}", parameters["current_step"], self.simulation_steps)

        all_devices, server, all_services = super().get_components()

        # Edge Device processing
        for edge_device in all_devices:
            if edge_device.id in self.edge_device_ids:
                Device.modify_power(edge_device, self.harvester, current_timestep, self.power_required)
                Device.modify_state(edge_device, self.harvester, current_timestep, self.min_power_threshold)

                Measurement.collect_temperature(edge_device, current_timestep)
                
                edge_device_services = [service for service in all_services if service.server.id == edge_device.id]
                if edge_device_services != []:
                    for service in edge_device_services:
                        if not edge_device.transfer_model["transfer"]:
                            AIModel.run(service, current_timestep)
                        else:
                            AIModel.stop(service, current_timestep)
                
                    Device.transfer_to_server(
                        edge_device=edge_device,
                        server=server,
                        timestep=current_timestep,
                        min_power_required=self.min_power_threshold,
                        offloading=self.offloading,
                        harvester=self.harvester
                    )

        # NEW Server processing
        results = Device.transfer_to_edge_device(
            server=server,
            all_edge_devices=all_devices,
            harvester=self.harvester,
            all_services=all_services,
            timestep=current_timestep,
            min_power_required=self.min_power_threshold,
            offloading=self.offloading,
            loadbalancing=self.loadbalancing
        )
        for result in results:
            if result["success"]:
                logger.bind(simulation=True).debug("Timestep: {} - LOADBALANCING - Transfer to Edge Device {} was successful.", current_timestep, result['edge_device_id'])

        Device.update_ongoing_transfers(
            offloading=self.offloading,
            all_devices=all_devices,
            server=server,
            timestep=current_timestep
        )

        self.harvester.next_timestep()

    def stopping_criterion(self, model: object):
        """
        Stopping criterion for the simulation after x iterations
        defined in config file 'simulation_steps'.
        """
        return super().stopping_criterion(model)

    def run(self):
        """
        Run the simulation with the defined strategy and offloading.
        """
        EdgeServer.collect = custom_collect_edge_server_proactive
        Service.collect = custom_collect_service

        super().run()
