"""Logging module for the loguru logger."""
import os
import sys
from loguru import logger

class Logging:
    """
    A logging utility class to configure and manage logging for different components of the system.
    Attributes:
        info (bool): Flag to enable logging at the INFO level.
        debug (bool): Flag to enable logging at the DEBUG level.
    Methods:
        __init__(info: bool, debug: bool) -> None:
            Initializes the Logging class, configures loggers based on the provided flags.
    """
    def __init__(self, info: bool, debug: bool) -> None:
        logger.remove()
        self._del_previous_logfiles()
        self._add_logging(info, debug)

    @classmethod
    def _del_previous_logfiles(cls) -> None:
        """
        Deletes the previous log files before starting the simulation.
        """
        log_files = [
            "log_analyzer.log",
            "device_status.log",
            "device_offloading.log",
            "energy_data.log",
            "energy_harvester.log",
            "energy_harvester_battery.log",
            "ai_model.log",
            "heartbeat_protocol.log",
            "loadbalancing.log",
            "measurement.log",
            "simulation.log",
            "battery_debug.log",
        ]
        for file in log_files:
            try:
                os.remove(os.path.join(os.path.dirname(__file__), "logfiles", file))
            except FileNotFoundError:
                # print(f"File {file} not found, skipping deletion.")
                continue
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

    @classmethod
    def _add_logging(cls, info: bool, debug: bool):
        """
        Configures the loggers based on the provided flags.
        """
        if info:
            logger.add(
                        sys.stderr,
                        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:^8}</level> | <cyan>{function:^18}</cyan> | <level>{message}</level>",
                        level="INFO",
                        backtrace=True,
                        diagnose=True
                    )
        if debug:
            log_levels = ["DEBUG", "INFO"]
            log_files = {
                "log_analyzer.log": "log_analyzer",
                "device_status.log": "status",
                "device_offloading.log": "offloading",
                "energy_data.log": "data",
                "energy_harvester.log": "harvester",
                "energy_harvester_battery.log": "battery",
                "ai_model.log": "ai_model",
                "heartbeat_protocol.log": "heartbeat",
                "loadbalancing.log": "loadbalancing",
                "measurement.log": "measurement",
                "simulation.log": "simulation",
                "battery_debug.log": "battery_debug",
            }
            for file, record_name in log_files.items():
                for level in log_levels:
                    logger.add(
                        sink=f"utils/logfiles/{file}",
                        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {function:^30} | {message}",
                        backtrace=True,
                        diagnose=True,
                        level=level,
                        filter=lambda record, rn=record_name: rn in record["extra"],
                    )
