from datetime import datetime

class ClinicBranch:
    """
    Represents a Hospital or Clinic Branch in the system.
    Demonstrates Encapsulation by protecting internal service lists, location, and operating hours.
    """
    def __init__(self, branch_id: int, name: str, location: str):
        self.__branch_id = branch_id
        self.name = name          # Uses setter for validation
        self.location = location  # Uses setter for validation
        self.__working_hours = {"start": "08:00", "end": "17:00"}
        self.__services = {}      # Stores medical services: {service_name: {"duration": int, "price": float}}
        self.__doctors = []       # Stores assigned doctor IDs or objects
