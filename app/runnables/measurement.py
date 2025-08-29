"""
Class which contains all the measurements that can be done on the data.
"""
import random
from loguru import logger

class Measurement:
    """
    A class to represent a measurement system.
    
    Methods
    -------
    - collect_temperature(edge_device: object, timestep: int) -> None
        
        Collect the temperature data from the Edge Device if it is in state "on".
    """
    @classmethod
    def collect_temperature(cls, edge_device: object, timestep: int) -> None:
        """
        Collect the temperature data if STATE == 'on' and TRANSFER == False.
        Args:
            edge_device (object): The edge device.
            timestep (int): The current timestep.
        """
        if edge_device.status["state"] == "on" and not edge_device.transfer_model["transfer"]:
            temperature = random.randint(0, 40)
            measurement = {
                "timestep": timestep,
                "temperature": temperature
            }
            edge_device.temperature_measurement.append(measurement)
            logger.bind(measurement=True).debug(
                "Timestep: {} - EdgeDevice: {} - Measured Temperature: {}",
                timestep, edge_device.id, temperature
            )
