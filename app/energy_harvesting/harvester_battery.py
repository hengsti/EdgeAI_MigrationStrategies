"""Energy Harvester Battery Module"""
from loguru import logger

from energy_harvesting import EnergyHarvester

class HarvesterBattery(EnergyHarvester):
    """
    Battery-backed energy harvester.
    Stores energy harvested from solar and wind, powers devices from battery.
    """
    def __init__(
        self,
        device_ids,
        ampere,
        volts,
        compute_energydata,
        efficiency=0.95,
        initial_charge=1.0,
        depth_of_discharge=0.25
    ):
        """
        Initialize the HarvesterBattery.

        Args:
            device_ids (list[int]): List of edge device IDs.
            ampere (float): Battery capacity in Ampere-hours (Ah).
            volts (float): Nominal voltage (V).
            compute_energydata (bool): Whether to use energy traces.
            efficiency (float): Charging efficiency (0.0–1.0). Default is 95%.
            initial_charge (float): Initial charge level (0.0–1.0). Default is 100%.
            depth_of_discharge (float): Minimum charge level (0.0–1.0). Default is 25%.
        """
        super().__init__(device_ids, compute_energydata)

        self.capacity_ah = ampere
        self.voltage = volts
        self.efficiency = efficiency

        # Max total energy that can be stored in Wh
        self.max_capacity_wh = round(self.capacity_ah * self.voltage, 2)

        # Battery State of Charge (BSOC or SOC) in Wh per device
        self.bsoc = {
            device_id: round((self.max_capacity_wh * initial_charge),2) for device_id in device_ids
        }

        # Depth of Discharge (DoD) in Wh per device
        self.dod = depth_of_discharge

        # Min BSOC - under which the battery should not be discharged to avoid damage
        self.min_bsoc = round(self.max_capacity_wh * self.dod,2)

        self.debug_init(self.max_capacity_wh * initial_charge)

    def get_energy(self, device_id: int) -> dict:
        """
        Returns the harvested energy at current timestep (not from battery).
        Useful for charging only.
        """
        return {
            "solar": round(self.solar_energy[device_id][self.current_time], 2),
            "wind": round(self.wind_energy[device_id][self.current_time], 2)
        }
    
    def get_bsoc(self, device_id: int) -> float:
        """
        Return the current battery state of charge (BSOC) in Wh.

        Args:
            device_id (int): The ID of the device.

        Returns:
            float: The battery state of charge in Wh.
        """
        return round(self.bsoc[device_id], 2)
    
    def get_max_capacity(self) -> float:
        """
        Return the maximum battery capacity in Wh.
        """
        return round(self.max_capacity_wh, 2)
    
    def get_min_bsoc(self) -> float:
        """
        Return the minimum BSOC in Wh.
        """
        return round(self.min_bsoc, 2)
    

    def get_highest_available_power(self, device_id: int) -> float:
        """
        Return power availability from the battery (not solar/wind directly).
        """
        energy = self.bsoc[device_id]
        return round(energy, 2)

    def charge_battery(self, device_id: int, timestep: int) -> None:
        """
        Charge the battery using available solar + wind power.

        Args:
            device_id (int): ID of the edge device.
            timestep_seconds (float): Duration of the timestep in seconds.
        """
        energy_data = self.get_energy(device_id)
        harvested_power = max(energy_data["solar"], energy_data["wind"])

        # Energy = Power * Time (converted from seconds to hours)
        energy_added_wh = round((harvested_power * 1) / 3600.0, 2)   # Convert to Wh
        energy_added_wh = round(energy_added_wh * self.efficiency, 2)  # Apply charging efficiency

        current_energy = self.bsoc[device_id]
        self.bsoc[device_id] = min(current_energy + energy_added_wh, self.max_capacity_wh)

        logger.bind(battery=True).debug(
            "Timestep {} - Device {}: Harvested Energy = {:.4f} Wh, BSOC = {:.2f} Wh",
            timestep, device_id, energy_added_wh, self.bsoc[device_id]
        )

    def consume_energy(self, device_id: int, required_power_w: float, timestep: int) -> bool:
        """
        Consume energy from the battery to power the device.

        Args:
            device_id (int): ID of the edge device.
            required_power_w (float): Required power in Watts.
            timestep_seconds (float): Timestep duration in seconds.

        Returns:
            bool: True if energy was available and consumed; False if not enough.
        """
        # self.__repr__(timestep)
        required_energy_wh = round((required_power_w * 1) / 3600.0, 2)  # Convert to Wh

        if self.bsoc[device_id] >= self.min_bsoc:
            self.bsoc[device_id] -= required_energy_wh
            if self.bsoc[device_id] < self.min_bsoc:
                logger.bind(battery=True).debug(
                    "Timestep {} - Device {} - Insufficient BSOC => DoD undercut - Needed {:.4f} Wh - BSOC/min_BSOC: {:.4f}/{:.4f} Wh",
                    timestep, device_id, required_energy_wh, self.bsoc[device_id], self.min_bsoc
                )
                return False

            logger.bind(battery=True).debug(
                "Timestep {} - Device {} - Consumed {:.4f}Wh -> BSOC/max.Capacity: {:.2f}/{:.2f} Wh",
                timestep, device_id, required_energy_wh, self.bsoc[device_id], self.max_capacity_wh
            )
            return True

        logger.bind(battery=True).debug(
            "Timestep {} - Device {} - Insufficient BSOC => DoD undercut - Needed {:.4f} Wh - BSOC/min_BSOC: {:.4f}/{:.4f} Wh",
            timestep, device_id, required_energy_wh, self.bsoc[device_id], self.min_bsoc
        )
        return False

    def next_timestep(self) -> None:
        """
        Increment the internal time index (same as base class).
        """
        self.current_time += 1

    def debug(self) -> None:
        """
        Print the current state of the battery.
        """
        for device_id, stored_wh in self.bsoc.items():
            logger.bind(battery=True).debug(
                "Battery level - Device {}: {:.2f}/{:.2f} Wh",
                device_id, stored_wh, self.max_capacity_wh
            )

    def debug_init(self, bsoc) -> None:
        """
        Print the initial state of the battery.
        """
        logger.bind(battery=True).debug(
            "Batteries initialized - Max_Capacity: {:.2f} Wh, BSOC: {:.2f} Wh, DoD: {:.2f} %",
            self.max_capacity_wh, bsoc, self.dod * 100.0
        )
    
    def __repr__(self, timestep):
        repr = f"Timestep {timestep}"
        for device_id, stored_wh in self.bsoc.items():
            repr += f"\nDevice {device_id}: {stored_wh:.2f}/{self.max_capacity_wh:.2f} Wh --> Battery is {'OK' if stored_wh > self.min_bsoc else 'LOW'}"
        logger.bind(battery_debug=True).debug("{}", repr)
        return repr
