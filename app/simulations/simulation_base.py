"""
Simulation moduel for oracle approach.
"""
import json
from loguru import logger
from edge_sim_py import Simulator, EdgeServer, Service

from logs import LogAnalyzer
from energy_harvesting import EnergyHarvester, HarvesterBattery
from runnables import AIModel, Measurement, HeartbeatProtocol, Loadbalancer
from devices import ReactiveDevice as Device
from utils import custom_collect_service, custom_collect_edge_server_reactive

class SimulationBase:
    """
    Simulation class for the oracle approach.
    """
    def __init__(self, config_variables):
        self.config_variables = config_variables
        self.simulation_steps = config_variables["simulation"]["steps"]
        self.tick_duration=self.config_variables["simulation"]["tick_duration"]
        self.tick_unit=self.config_variables["simulation"]["tick_unit"]
        self.format_logs = config_variables["format_logs"]

        self.strategy = config_variables["strategy"]
        self.offloading = config_variables["offloading"]

        self.topology = config_variables["topology"]

        if self.topology == "test":
            self.edge_device_ids = config_variables["edge_device_ids"]["test"]
            self.topology_file = f"topologies/{self.strategy}/test.json"
        elif self.topology == "prod":
            self.edge_device_ids = config_variables["edge_device_ids"]["prod"]
            self.topology_file = f"topologies/{self.strategy}/prod.json"

        self.loadbalancing = config_variables["loadbalancing"]

        logger.bind(simulation=True).info(
            "Simulation Details - strategy: {} - offloading: {} - topology: {} - loadbalancing: {}",
            self.strategy, self.offloading, self.topology, self.loadbalancing
        )

        self.server_id = config_variables["server_id"]

        logger.bind(simulation=True).info("...loading energy harvester...")
        self.compute_energydata = self.config_variables["compute_energydata"]
        self.battery_mode = config_variables["battery"]["enabled"]
        if self.battery_mode:
            logger.bind(simulation=True).info("Battery mode is enabled")
            self.battery_ampere_hours = config_variables["battery"]["characteristics"]["ampere_hours"]
            self.battery_voltage = config_variables["battery"]["characteristics"]["voltage"]
            self.efficiency = config_variables["battery"]["characteristics"]["efficiency"]
            self.initial_charge = config_variables["battery"]["characteristics"]["initial_charge"]
            self.depth_of_discharge = config_variables["battery"]["characteristics"]["depth_of_discharge"]
            
            self.harvester = HarvesterBattery(
                self.edge_device_ids,
                ampere=self.battery_ampere_hours,
                volts=self.battery_voltage,
                compute_energydata=self.compute_energydata,
                efficiency=self.efficiency,
                initial_charge=self.initial_charge,
                depth_of_discharge=self.depth_of_discharge
            )
        else:
            logger.bind(simulation=True).info("Battery mode is disabled")
            self.harvester = EnergyHarvester(self.edge_device_ids, self.compute_energydata)

        self.power_required = round(config_variables["battery"]["power_required"], 2)

        logger.bind(simulation=True).info("Simulation initialized successfully")
        logger.bind(simulation=True).info("Progress - Timestep:   0/{}", self.simulation_steps)
        
    def get_components(self):
        """
        Get all devices and services in the simulation.

        Returns:
            all_devices (list): List of all devices in the simulation.
            server (EdgeServer): The server instance.
            all_services (list): List of all services in the simulation.
        """
        all_devices = EdgeServer.all()
        server = next((server for server in all_devices if server.id == self.server_id), None)
        if server is None:
            raise ValueError("Server not found")
        all_services = Service.all()
        
        return all_devices, server, all_services

    def update_simulation(self, parameters: dict) -> None:
        """
        Logic for updating the simulation at each timestep.
        """
        print("needs to be implemented")

    def stopping_criterion(self, model: object):
        """
        Stopping criterion for the simulation after x iterations
        defined in config file 'simulation_steps'.
        """
        return model.schedule.steps == self.simulation_steps

    def run(self):
        """
        Run the simulation with the defined strategy and offloading.
        """
        simulator = Simulator(
            tick_duration=self.tick_duration,
            tick_unit=self.tick_unit,
            stopping_criterion=self.stopping_criterion,
            resource_management_algorithm=self.update_simulation
        )

        simulator.initialize(input_file=self.topology_file)
        simulator.run_model()
        logger.bind(simulation=True).success("Simulation completed successfully after {} steps.", self.simulation_steps)
        
        if self.format_logs:
            LogAnalyzer.analyze_logs(self.strategy, self.offloading)
            logger.bind(simulation=True).debug("Logs have been formatted and saved to logs_formatted directory")
