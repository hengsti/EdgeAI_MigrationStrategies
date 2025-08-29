"""
This script loads the config.yaml file and sets up the configuration for the project.
"""
import sys
import yaml

class Config:
    """
    Class to load the configuration file and return the configuration variables.
    """
    def __init__(self, config_file: str):
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config - Error: The file {config_file} was not found.")
            sys.exit(1)
        except yaml.YAMLError:
            print(f"Config - Error: The file {config_file} is not a valid YAML.")
            sys.exit(1)
        except Exception as e:
            print(f"Config - An unexpected error occurred: {e}")
            sys.exit(1)

    def get(self):
        """
        Function to return the configuration variables.
        Returns:
            dict: The configuration variables.
        """
        return self.config

    def validate(self):
        """
        Function to validate the configuration variables.
        Raises:
            ValueError: If the configuration variables are not valid.
        """
        required_keys = [
            "info",
            "debug",
            "offloading",
            "topology",
            "strategy",
            "loadbalancing",
            "compute_energydata"
        ]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Config - Missing required key: {key}")
            
        if "simulation" not in self.config or "steps" not in self.config["simulation"]:
            raise ValueError("Config - Missing required key: simulation.steps")
        
        if "min_power_threshold" not in self.config["proactive"]:
            raise ValueError("Config - Missing required key: proactive.min_power_threshold")
        
        if "reactive" not in self.config or "max_services_per_device" not in self.config["reactive"]:
            raise ValueError("Config - Missing required key: reactive.max_services_per_device")
        if "oracle" not in self.config or "max_services_per_device" not in self.config["oracle"]:
            raise ValueError("Config - Missing required key: oracle.max_services_per_device")

        if self.config["offloading"] not in ('model', 'data'):
            raise ValueError("Config - Invalid input for [offloading]!\t-->\tInputs: model, data.")
        if self.config["topology"] not in ('test', 'prod'):
            raise ValueError("Config - Invalid input for [topology]!\t-->\tInputs: test, prod.")
        if self.config["strategy"] not in ('reactive', 'proactive', 'oracle'):
            raise ValueError("Config - Invalid input for [strategy]!\t-->\tInputs: reactive, proactive, oracle.")

        if not isinstance(self.config["loadbalancing"], bool):
            raise ValueError("Config - Invalid input for [loadbalancing]!\t-->\tInputs: True, False.")
        if not isinstance(self.config["compute_energydata"], bool):
            raise ValueError("Config - Invalid input for [compute_energydata]!\t-->\tInputs: True, False.")
        if not isinstance(self.config["simulation"]["steps"], int) or self.config["simulation"]["steps"] <= 0:
            raise ValueError("Config - Invalid input for [steps]!\t-->\tMust be a positive integer.")
        if not isinstance(self.config["proactive"]["min_power_threshold"], (int, float)) or self.config["proactive"]["min_power_threshold"] <= 0:
            raise ValueError("Config - Invalid input for [proactive][min_power_threshold]!\t-->\tMust be a positive number (int, float).")
        if not isinstance(self.config["reactive"]["max_services_per_device"], int) or self.config["reactive"]["max_services_per_device"] <= 0:
            raise ValueError("Config - Invalid input for [reactive][max_services_per_device]!\t-->\tMust be a positive integer.")
        if not isinstance(self.config["oracle"]["max_services_per_device"], int) or self.config["oracle"]["max_services_per_device"] <= 0:
            raise ValueError("Config - Invalid input for [oracle][max_services_per_device]!\t-->\tMust be a positive integer.")

        if self.config["strategy"] == "reactive":
            if self.config["reactive"]["max_services_per_device"] > 10:
                print("Config - Warning: The value for [max_services_per_device] is higher then the amount of services!")
            
        if self.config["battery"]["enabled"] and self.config["proactive"]["min_power_threshold"] >= self.config["battery"]["power_required"]:
            raise ValueError("Config - Invalid input for [proactive][min_power_threshold]!\t-->\tMust be lower than the battery power required.")
