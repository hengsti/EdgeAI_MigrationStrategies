"""
File to define the data collectors for the simulator.
"""
def custom_collect_service(self):
    """
    Collect the data from the service.
    """
    data = {
        "model_id": self.id,
        "model_name": self.label,
        "device_id": self.server.id,
        "state": self.state,
        "program_counter": self.program_counter,
        "trained": self.trained,
        "max_training_time": self.max_training_time,
        "actual_training_time": self.actual_training_time,
        "max_prediction_time": self.max_prediction_time,
        "actual_prediction_time": self.actual_prediction_time,
        "predictions_counter": self.predictions_counter
    }
    return data

def custom_collect_edge_server_proactive(self):
    """
    Collect the data from the edge server.
    """
    data = {
        "model_name": self.model_name,
        "model_type": self.model_type,
        "service_ids": [service.id for service in self.services],
        "power_source": self.power_source,
        "actual_power": self.actual_power,
        "active": self.status["active"],
        "state": self.status["state"],
        "temperature_measurements": [measurement["temperature"] for measurement in self.temperature_measurement],
        "transfer": self.transfer_model["transfer"],
        "trans_service_ids": [service_id for service_id in self.transfer_model.get("transfer_service_ids", [])],
        "transfer_duration": self.transfer_model["transfer_duration"],
        "transfer_time": self.transfer_model["transfer_time"],
        "transfer_to_device_id": self.transfer_model["transfer_to_device_id"],
        "transfer_from_device_id": self.transfer_model["transfer_from_device_id"],
        "failed_transfers": self.transfer_model["transfer_failed"]
    }
    return data

def custom_collect_edge_server_reactive(self):
    """
    Collect the data from the edge server.
    """
    data = {
        "model_name": self.model_name,
        "model_type": self.model_type,
        "service_ids": [service.id for service in self.services],
        "power_source": self.power_source,
        "actual_power": self.actual_power,
        "active": self.status["active"],
        "state": self.status["state"],
        "temperature_measurements": [measurement["temperature"] for measurement in self.temperature_measurement],
    }
    return data
