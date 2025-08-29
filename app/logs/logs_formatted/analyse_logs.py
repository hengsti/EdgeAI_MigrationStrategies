"""
Log Vizualizer Module
"""
import os

import pandas as pd
import msgpack
from loguru import logger

class LogAnalyzer:
    """
    A class used to analyze and format log files.
    
    Methods
    -------
    - analyze_logs(cls, strategy: str, offloading: str) -> None:
        
        Analyzes log files in the 'logs' directory, converts them to DataFrames,
        and saves the formatted data to CSV files in the 'logs_formatted' directory.
    """
    @classmethod    
    def analyze_logs(cls, strategy: str, offloading: str) -> None:
        """
        Analyzes log files in the 'logs' directory, converts them to DataFrames, 
        and saves the formatted data to CSV files in the 'logs_formatted' directory.
        This method performs the following steps:
        1. Identifies all '.msgpack' files in the 'logs' directory.
        2. Reads each '.msgpack' file and converts its content to a pandas DataFrame.
        3. Saves the DataFrame for 'EdgeServer' to 'logs_formatted/edgeServer_output.csv'.
        4. Saves the DataFrame for 'Service' to 'logs_formatted/service_output.csv'.
        5. Logs an informational message indicating that the logs have been formatted and saved.
        Raises:
            FileNotFoundError: If the 'logs' directory does not exist.
            Exception: If there is an error reading the '.msgpack' files or saving the CSV files.
        """
        logs_directory = f"{os.getcwd()}/logs"
        dataset_files = [file for file in os.listdir(logs_directory) if ".msgpack" in file]

        datasets = {}
        for file in dataset_files:
            with open(f"logs/{file}", "rb") as data_file:
                datasets[file.replace(".msgpack", "")] = pd.DataFrame(msgpack.unpackb(data_file.read(), strict_map_key=False))

        datasets["EdgeServer"].to_csv(f'logs/logs_formatted/{strategy}/{offloading}/edgeServer_output.csv', index=False)
        logger.bind(log_analyzer=True).debug("edgeServer_output.csv saved to logs_formatted directory")
        datasets["Service"].to_csv(f'logs/logs_formatted/{strategy}/{offloading}/service_output.csv', index=False)
        logger.bind(log_analyzer=True).debug("service_output.csv saved to logs_formatted directory")
