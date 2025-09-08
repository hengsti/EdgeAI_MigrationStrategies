"""
AI Model methods to train and predict the measurment model.
"""
from loguru import logger

class AIModel:
    """
    A class used to represent an AI Model with training and prediction capabilities.
    
    Methods
    -------
    - run(service: object) -> None
        
        Runs the AI model by training, predicting, and increasing the program counter.
        
    - stop(service: object) -> None
    
        Stops the AI model by setting the service state to stopped.
    """
    @classmethod
    def run(cls, service: object, timestep: int) -> None:
        """
        Run the AI model.
        """
        logger.bind(ai_model=True).debug(
            "Timestep: {} - Running AI Model {}",
            timestep, service.label
        )
        cls._state_running(service)
        cls.train_model(service)
        cls.predict(service)
        cls.increase_program_counter(service)

    @classmethod
    def stop(cls, service: object, timestep: int) -> None:
        """
        Stop the AI model.
        """
        logger.bind(ai_model=True).debug(
            "Timestep: {} - Stopping AI Model {}",
            timestep, service.label
        )
        cls._state_stopping(service)

    @classmethod
    def train_model(cls, service: object) -> None:
        """
        Train the AI model.
        Args:
            service (object): The AI model service.
        """
        if service.trained:
            logger.bind(ai_model=True).debug(
                "Model {} has already been trained",
                service.label
            )
            return

        if service.actual_training_time == service.max_training_time and not service.trained:
            service.trained = True
            logger.bind(ai_model=True).debug(
                "Model {} has been trained",
                service.label
            )
            service.actual_training_time = 0
            logger.bind(ai_model=True).debug(
                "Actual Training Time reset: {}",
                service.actual_training_time
            )
            return

        service.actual_training_time += 1
        logger.bind(ai_model=True).debug(
            "Training Model {} at timestamp: {}",
            service.label, service.actual_training_time
        )

    @classmethod
    def predict(cls, service: object) -> None:
        """
        Predict the measurement based on trained model.
        """
        if not service.trained:
            logger.bind(ai_model=True).debug(
                "Model {} has not been trained yet",
                service.label
            )
            return

        if service.trained and service.actual_prediction_time < service.max_prediction_time:
            service.actual_prediction_time += 1
            logger.bind(ai_model=True).debug(
                "Predicting Model {} at timestamp: {}",
                service.label, service.actual_prediction_time
            )

        if service.actual_prediction_time == service.max_prediction_time:
            service.predictions_counter += 1
            logger.bind(ai_model=True).debug(
                "Model {} has completed prediction cycle {}",
                service.label, service.predictions_counter
            )
            service.actual_prediction_time = 0
            logger.bind(ai_model=True).debug(
                "Predicted Timestamp reset: {}",
                service.actual_prediction_time
            )

    @classmethod
    def increase_program_counter(cls, service: object) -> None:
        """
        Increase the program counter of the service.
        """
        service.program_counter += 1
        logger.bind(ai_model=True).debug(
            "Program Counter of Model {} increased to {}",
            service.label, service.program_counter
        )

    @classmethod
    def _state_running(cls, service: object) -> None:
        """
        Set the state of the service to running.
        """
        service.state = "running"
        logger.bind(ai_model=True).debug(
            "Service {} is running",
            service.label
        )

    @classmethod
    def _state_stopping(cls, service: object) -> None:
        """
        Set the state of the service to running.
        """
        service.state = "stopped"
        logger.bind(ai_model=True).debug(
            "Service {} is stopped",
            service.label
        )
