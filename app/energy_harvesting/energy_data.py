"""
helper module for loading energy data
"""
import time
import pandas as pd
from loguru import logger

def clean_data(data: pd.Series) -> pd.Series:
    """
    Clean the data by removing any missing values.
    Args:
        data (pd.Series): The data to be cleaned.
    Returns:
        pd.Series: The cleaned data.
    """
    # Convert to numeric, coercing errors to NaN
    numeric_data = pd.to_numeric(data, errors='coerce')
    # Fill NaN values with 0 or another appropriate value
    cleaned_data = numeric_data.fillna(0)
    return cleaned_data

def load_energy_data(file: str, filetype: str) -> pd.Series:
    """
    Load the energy data from the xlsx file.
    Args:
        file (str): The path to the xlsx file.
        type (str): The type of the file. It can be either "csv" or "excel".
    Returns:
        pd.Series: The wind speed and solar energy data.
    """
    start_time = time.time()
    if filetype == "csv":
        data = pd.read_csv(file)
    elif filetype == "excel":
        data = pd.read_excel(file)
    else:
        raise ValueError("Invalid file type. Please provide a valid file type.")
    end_time = time.time()
    execution_time = round(end_time - start_time, 4)
    logger.bind(data=True).debug(
        "Loaded energy data from {} in {} seconds.",
        file, execution_time
    )

    wind_speed =  pd.Series(data["WindSpeed"])     # Wind speed in m/s
    wind_speed_cleaned = clean_data(wind_speed)

    solar_energy = pd.Series(data["SolarEnergy"])  # Solar energy in Langley
    solar_energy_cleaned = clean_data(solar_energy)

    logger.bind(data=True).debug(
        "Loaded Wind {} and Solar {} data points.",
        len(wind_speed_cleaned), len(solar_energy_cleaned)
    )

    return wind_speed_cleaned, solar_energy_cleaned

def calc_actual_solar_power(solar_energy: pd.Series) -> pd.Series:
    """
    Convert the solar energy from Langley to Watt.
    Args:
        solar_energy (pd.Series): The solar energy in Langley.
    Model:
        1 Langley = 11.622 Wh/m^2
        Assuming our solar panel has 1 m^2 area.
    Returns:
        pd.Series: The acutal solar energy in Watt to each time measurement.
    """
    # 1 Langley = 11.622 Wh/m^2
    solar_energy_watt = solar_energy * 11.622
    solar_energy_watt = solar_energy_watt.rename("SolarPower(W)")
    return solar_energy_watt

def calc_actual_wind_power(wind_speed: pd.Series) -> pd.Series:
    """
    Calculate the wind power in Watt.
    Args:
        wind_energy (pd.Series): The wind speed in m/s.
    Model:
        Wind power in Watt = 0.5 * air density * swept area * wind speed^3 * Power Coefficient * Generator Efficiency
        air density = 1.225 kg/m^3
        swept area of turbine blades = 0.5 m^2
        Power Coefficient = 0.35
        Generator Efficiency = 0.9
    Returns:
        pd.Series: The actual wind power in Watt to each time measurement.
    """
    air_density = 1.225
    swept_area = 0.5
    power_coefficient = 0.35
    generator_efficiency = 0.90

    wind_power = 0.5 * air_density * swept_area * wind_speed ** 3 * power_coefficient * generator_efficiency
    wind_power = wind_power.rename("WindPower(W)")
    return wind_power

def store_data_in_file(wind_power: pd.Series, solar_power: pd.Series) -> None:
    """
    Store energy data in a high-performance format (Parquet) for fast processing with Pandas.
    
    Args:
        wind_power (pd.Series): The wind power in Watt.
        solar_power (pd.Series): The solar power in Watt.
    """
    file_path = "./data/energy_data.parquet"

    # Combine the data into a DataFrame
    df = pd.concat([wind_power, solar_power], axis=1)

    # Store as Parquet with compression
    df.to_parquet(file_path, engine='pyarrow', compression='snappy', index=False)
    logger.bind(data=True).debug("Stored energy data to {} as Parquet file.", file_path)

def load_energy_data_parquet(file: str) -> tuple[pd.Series, pd.Series]:
    """
    Load wind and solar power data from a Parquet file.
    
    Args:
        file (str): Path to the Parquet file.
    
    Returns:
        tuple[pd.Series, pd.Series]: Wind and solar power data as separate Series.
    """
    df = pd.read_parquet(file)
    return df["WindPower(W)"], df["SolarPower(W)"]


# if __name__ == "__main__":
#     wind_speed, solar_energy = load_energy_data("./data/Weather Data 2014-11-30.xlsx", "excel")
#     wind_power = calc_actual_wind_power(wind_speed)
#     solar_power = calc_actual_solar_power(solar_energy)
#     store_data_in_file(wind_power, solar_power)
#     logger.info("Energy data processing completed.")