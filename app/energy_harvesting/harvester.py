"""
EnergyHarvester module
"""
import pandas as pd
from loguru import logger

from energy_harvesting.energy_data import load_energy_data, calc_actual_solar_power, calc_actual_wind_power, load_energy_data_parquet

class EnergyHarvester:
    """
    A class to represent an energy harvester that collects energy from solar and wind sources.
    
    Attributes
    ----------
    - solar_energy : pd.Series
        A pandas Series containing solar energy data.
        
    - wind_speed : pd.Series
        A pandas Series containing wind speed data.
        
    - current_time : int
        An integer representing the current time index for accessing energy data.
    
    Methods
    -------
    - consume_energy():
        Returns a dictionary with the available solar and wind power at the current time index.
        
    - next_timestep():
        Increments the current time index by 1.
        
    - get_highest_available_power():
        Returns the highest available power from solar and wind sources.
        
    - get_power_forecast(forecast_time: int):
        Returns the power forecast for solar and wind sources at the specified time index.
    """
    def __init__(self, device_ids: list, compute_energydata: bool = False):
        self.device_ids = device_ids
        self.current_time = 0

        if compute_energydata:
            wind_speed, solar_energy = load_energy_data("./data/Weather Data 2014-11-30.xlsx", "excel")
            self.solar_energy = self.split_energy_data(self.init_solar_energy(solar_energy), device_ids)
            self.wind_energy = self.split_energy_data(self.init_wind_speed(wind_speed), device_ids)
        else:
            wind_power, solar_power = load_energy_data_parquet("./data/energy_data.parquet")
            self.wind_energy = self.split_energy_data(wind_power, device_ids)
            self.solar_energy = self.split_energy_data(solar_power, device_ids)

    def split_energy_data(self, energy_data: pd.Series, device_ids: list) -> dict:
        """
        Split the energy data into a dictionary of device IDs and corresponding energy data.
        Args:
            energy_data (pd.Series): A pandas Series containing energy data.
            device_ids (list): A list of device IDs.
        Returns:
            dict: A dictionary of device IDs and corresponding energy data.
        """
        num_devices = len(device_ids)
        split_data = {}
        chunk_size = len(energy_data) // num_devices

        logger.bind(harvester=True).debug(
            "num_devices: {} - chunk_size: {}",
            num_devices, chunk_size
        )

        for i, device_id in enumerate(device_ids):
            start_index = i * chunk_size
            end_index = start_index + chunk_size if i != num_devices - 1 else len(energy_data)
            split_data[device_id] = energy_data[start_index:end_index].reset_index(drop=True)

        return split_data

    def init_solar_energy(self, solar_energy: pd.Series) -> pd.Series:
        """
        Get the solar energy data.
        Args:
            solar_energy (pd.Series): A pandas Series containing solar energy data.
        Returns:
            pd.Series: A pandas Series containing actual solar power data.
        """
        return calc_actual_solar_power(solar_energy)

    def init_wind_speed(self, wind_speed: pd.Series) -> pd.Series:
        """
        Get the wind speed data.
        Args:
            wind_speed (pd.Series): A pandas Series containing wind speed data.
        Returns:
            pd.Series: A pandas Series containing actual wind power data.
        """
        return calc_actual_wind_power(wind_speed)

    def get_energy(self, device_id: int) -> dict:
        """
        Get the available solar and wind power at the current time index.
        Args:
            device_id (int): An integer representing the device ID.
        Returns:
            dict: A dictionary with the available solar and wind power at the current time index.
        """
        return {
            "solar": round(self.solar_energy[device_id][self.current_time], 2),
            "wind": round(self.wind_energy[device_id][self.current_time], 2)
        }

    def next_timestep(self) -> None:
        """
        Increment the current time index by 1.
        """
        self.current_time += 1

    def get_highest_available_power(self, device_id: int) -> float:
        """
        Get the highest available power from solar and wind sources.
        Args:
            device_id (int): An integer representing the device ID.
        Returns:
            float: The highest available power from solar and
        """
        return max(self.solar_energy[device_id][self.current_time], self.wind_energy[device_id][self.current_time])

    def get_power_forecast(self, device_id: int, forecast_time: int) -> float:
        """
        Get the power forecast for solar and wind sources.
        Args:
            device_id (int): An integer representing the device ID.
            forecast_time (int): An integer representing the forecast time index.
        Returns:
            float: The highest power for forecast of solar and wind sources.
        """
        return max(self.solar_energy[device_id][self.current_time + forecast_time], self.wind_energy[device_id][self.current_time + forecast_time])

    def debug_solar_energy(self, device_ids: list) -> None:
        """
        Debug the solar energy data.
        Args:
            device_ids (list): A list of device IDs.
        """
        debug_data = pd.DataFrame({device_id: self.solar_energy[device_id] for device_id in device_ids})
        debug_data.to_csv("energy_harvesting/debug/solar_energy_debug.csv", index=False)
        
    def debug_wind_speed(self, device_ids: list) -> None:
        """
        Debug the wind speed data.
        Args:
            device_ids (list): A list of device IDs.
        """
        debug_data = pd.DataFrame({device_id: self.wind_energy[device_id] for device_id in device_ids})
        debug_data.to_csv("energy_harvesting/debug/wind_energy_debug.csv", index=False)
