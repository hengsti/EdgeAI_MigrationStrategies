"""
This is the main file to run the simulation.
It reads the configuration file and 
runs the simulation based on the strategy defined in the configuration file.
The simulation can be either reactive or proactive.
The simulation is run by creating an instance of the SimulationReactive or
SimulationProactive class andcalling the run method.
"""
from loguru import logger

from utils import Logging, Config
from simulations import SimulationReactive, SimulationProactive, SimulationOracle

def main(config_file: str = 'config.yaml') -> bool:
    """
    Main function to load configuration and run the simulation based on the strategy defined.
    This function performs the following steps:
    1. Loads the configuration variables by calling `setup_config()`.
    2. Checks the strategy defined in the configuration file.
    3. Initializes the logger based on the configuration variables.
    4. Runs the appropriate simulation based on the strategy:
       - If the strategy is `reactive`, it initializes and runs `SimulationReactive`.
       - If the strategy is `proactive`, it initializes and runs `SimulationProactive`.
       - If the strategy is `oracle`, it initializes and runs `SimulationOracle`.
    5. Raises a `ValueError` if the strategy is invalid.
    Raises:
        ValueError: If the strategy defined in the configuration file is wrong.
    """
    try:
        config = Config(config_file)
        config.validate()
        config_variables = config.get()

        Logging(config_variables["info"], config_variables["debug"])

        if config_variables["strategy"] == "reactive":
            simulation = SimulationReactive(config_variables)
            simulation.run()
        if config_variables["strategy"] == "proactive":
            simulation = SimulationProactive(config_variables)
            simulation.run()
        if config_variables["strategy"] == "oracle":
            simulation = SimulationOracle(config_variables)
            simulation.run()

        return True
    except ValueError as e:
        logger.critical(e)
        return False

if __name__ == "__main__":
    main()
