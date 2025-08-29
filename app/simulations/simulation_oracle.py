"""
Simulation moduel for oracle approach.
"""
from loguru import logger
from edge_sim_py import Simulator, EdgeServer, Service

from logs import LogAnalyzer
from energy_harvesting import EnergyHarvester, HarvesterBattery
from runnables import AIModel, Measurement, HeartbeatProtocol, Loadbalancer
from devices import ReactiveDevice as Device
from utils import custom_collect_service, custom_collect_edge_server_reactive

from simulations.simulation_base import SimulationBase

class SimulationOracle(SimulationBase):
    """
    Simulation class for the oracle approach.
    """
    def __init__(self, config_variables):
        super().__init__(config_variables)
        
        self.max_services = config_variables["oracle"]["max_services_per_device"]
        
        # Analysis variables
        self.transfer_initiated = 0
        self.transfer_to_partner = 0

    def update_simulation(self, parameters: dict) -> None:
        """
        Logic for updating the simulation at each timestep.
        """
        current_timestep = parameters["current_step"]
        if parameters["current_step"] % 100 == 0:
            logger.bind(simulation=True).info("Progress - Timestep: {}/{}", parameters["current_step"], self.simulation_steps)

        all_devices, server, all_services = super().get_components()

        # edge device logic
        for edge_device in all_devices:
            if edge_device.id in self.edge_device_ids:
                # call power model and compute power logic
                Device.modify_power(edge_device, self.harvester, current_timestep, self.power_required)
                Device.modify_state(edge_device, self.harvester, current_timestep)
                # call measurement to collect temperature
                Measurement.collect_temperature(edge_device, current_timestep)
                for service in all_services:
                    if service.server.id == edge_device.id:
                        if edge_device.status["active"]:
                            # call AI model computation
                            AIModel.run(service, current_timestep)
                        else:
                            AIModel.stop(service, current_timestep)

        # server logic
        for edge_device in all_devices:
            if edge_device.id in self.edge_device_ids:
                # Heartbeat Protocol call
                # if heartbeat false, then call partner edge device to proceed with computing
                heartbeat, partner_edge_devices = HeartbeatProtocol.run(edge_device, all_devices, self.max_services, current_timestep)
                if self.offloading == "model":
                    if not heartbeat and len(edge_device.services) > 0:
                        self.transfer_initiated += 1
                    if partner_edge_devices is not None and len(edge_device.services) > 0:
                        self.transfer_to_partner += 1
                        # assign the model/data to the partner edge device
                        Device.assign_checkpoint_edge_device_to_server(
                            edge_device=edge_device,
                            server=server,
                            all_services=all_services,
                            offloading=self.offloading,
                            timestep=current_timestep
                        )
                        Device.assign_checkpoint_server_to_edge_device(
                            server=server,
                            partner_edge_devices=partner_edge_devices,
                            all_services=all_services,
                            offloading=self.offloading,
                            max_services=self.max_services,
                            timestep=current_timestep
                        )
                if self.offloading == "data":
                    if not heartbeat and len(edge_device.temperature_measurement) > 0:
                        self.transfer_initiated += 1
                    if partner_edge_devices is not None and len(edge_device.temperature_measurement) > 0:
                        self.transfer_to_partner += 1
                        # assign the data to the partner edge device
                        Device.assign_checkpoint_edge_device_to_server(
                            edge_device=edge_device,
                            server=server,
                            all_services=all_services,
                            offloading=self.offloading,
                            timestep=current_timestep
                        )
                        Device.assign_checkpoint_server_to_edge_device(
                            server=server,
                            partner_edge_devices=partner_edge_devices,
                            all_services=all_services,
                            offloading=self.offloading,
                            max_services=self.max_services,
                            timestep=current_timestep
                        )

        # load balancing logic
        if self.loadbalancing and self.offloading == "model":
            for edge_device in all_devices:
                if edge_device.id in self.edge_device_ids:
                    service_ids = [service.id for service in edge_device.services]
                    num_services = len(service_ids)
                    if num_services > edge_device.specifications["cpu_cores"] - edge_device.specifications["reserved_cpu_cores"]:
                        # call load balancer to check if the edge device can offload
                        partner_devices, servs = Loadbalancer.run(
                            edge_device=edge_device,
                            num_services=num_services,
                            all_devices=all_devices,
                            timestep=current_timestep
                        )
                        if partner_devices:
                            # assign the model/data to the partner edge device
                            Device.assign_checkpoint_edge_device_to_server(
                                edge_device=edge_device,
                                server=server,
                                all_services=servs,
                                offloading=self.offloading,
                                timestep=current_timestep
                            )
                            Device.assign_checkpoint_server_to_edge_device(
                                server=server,
                                partner_edge_devices=partner_devices,
                                all_services=servs,
                                offloading=self.offloading,
                                max_services=self.max_services,
                                timestep=current_timestep
                            )

        # update energy harvester to the next timestep
        self.harvester.next_timestep()

    def stopping_criterion(self, model: object):
        """
        Stopping criterion for the simulation after x iterations
        defined in config file 'simulation_steps'.
        """
        # return model.schedule.steps == self.simulation_steps
        return super().stopping_criterion(model)

    def run(self):
        """
        Run the simulation with the defined strategy and offloading.
        """
        EdgeServer.collect = custom_collect_edge_server_reactive
        Service.collect = custom_collect_service

        super().run()
        
        logger.bind(simulation=True).info(
            "Simulation Details:\nmax services per device: {} - loadbalancing: {}\nTotal Transfers to partner devices: {}, Successfull Transfers: {}, Failed Transfers: {}",
            self.max_services, self.loadbalancing, self.transfer_initiated, self.transfer_to_partner, self.transfer_initiated - self.transfer_to_partner
        )

