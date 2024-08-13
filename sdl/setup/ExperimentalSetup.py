import json
import os
import time
from datetime import datetime

import requests
import serial
from Arduino import Arduino
from neomodel import db

from mat2devplatform.settings import BASE_DIR
from matgraph.models.matter import Material
from matgraph.models.properties import Property
from sdl.models import Opentron_Module, ArduinoBoard


class BaseSetup:
    def __init__(self, config_source, db_model):
        """
        Initialize the base experimental setup with configuration source and database model.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.
            db_model (Model): Django model for database operations.
        """
        self.config_source = self.load_configuration(config_source)
        self.setup_model = db_model
        self.config = None
        self.name_space = None  # needs to be implemented in subclass
        self.simulate = False

    def load_config(self):
        """
        Load configuration from the specified source.
        """
        self.config = self.load_configuration(self.config_source)

    def load_configuration(self, config_source):
        """
        Load configuration from various sources: dict, file path, model, or URL.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.

        Returns:
            dict: The loaded configuration as a dictionary.

        Raises:
            ValueError: If the config source type is unsupported.
        """
        if isinstance(config_source, dict):
            return config_source
        elif isinstance(config_source, str):
            if config_source.startswith(('http://', 'https://')):
                response = requests.get(config_source)
                response.raise_for_status()
                return response.json()
            else:
                with open(config_source, 'r') as file:
                    return json.load(file)
        elif hasattr(config_source, 'get_config'):
            return config_source.get_config()
        else:
            raise ValueError("Unsupported configuration source type")

    def validate_config(self):
        """
        Validate the configuration settings.
        """
        # Implement validation logic if needed
        pass

    def save(self, **kwargs):
        """
        Store data in the database using Django ORM.

        Args:
            **kwargs: Key-value pairs of model fields and values.

        Returns:
            obj (Model): Saved Django model instance.
        """
        obj = self.setup_model(**kwargs)
        self.setup_model = obj
        obj.save()
        return obj

    def setup(self):
        """
        Load configuration, validate it, perform setup, and store results.
        """
        self.load_config()
        self.validate_config()
        self.perform_setup()
        self.store()

    def perform_setup(self):
        """
        Abstract method to be implemented by subclasses for specific setup tasks.
        """
        raise NotImplementedError


class SDLSetup(BaseSetup):
    def __init__(self, config_source, model):
        """
        Initialize the SDL setup with configuration source and model.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.
            model (Model): Django model for database operations.
        """
        super().__init__(config_source = config_source, db_model = model)
        self._setup_id = None
        self._user = None

    def setup(self, simulate=False):
        """
        Load configuration and set up SDL.
        """
        self.simulate = simulate
        self.load_config()
        self.setup_sdl()

    def setup_sdl(self):
        """
        Set up SDL including generating a setup ID and initializing the robot.
        """
        return NotImplementedError

    @property
    def setup_id(self):
        return self._setup_id

    @setup_id.setter
    def setup_id(self, value):
        return NotImplementedError

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    def initialize_platform(self):
        """
        Placeholder method for robot initialization.
        """
        return NotImplementedError




class ExternalDeviceSetup(BaseSetup):
    def __init__(self, config_source):
        """
        Initialize the external device setup with configuration source.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.
        """
        super().__init__(config_source, None)
        self.devices = []

    def setup(self):
        """
        Load configuration, validate it, and set up external devices.
        """
        self.load_config()
        self.validate_config()
        self.setup_devices()

    def setup_devices(self):
        """
        Initialize and configure external devices.
        """
        for device_config in self.config['labware']:
            device = self.initialize_device(device_config)
            self.validate_device(device)
            self.devices.append(device)

    def initialize_device(self, device_config):
        """
        Initialize an external device.

        Args:
            device_config (dict): Configuration for the device.
        """
        pass

    def validate_device(self, device):
        """
        Validate the device configuration.

        Args:
            device (dict): Device configuration.
        """
        pass


