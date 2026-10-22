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
# --- Properties (Getters & Setters) ---
    @property
    def branch_id(self) -> int:
        return self.__branch_id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, new_name: str):
        if new_name and new_name.strip():
            self.__name = new_name.strip()
        else:
            raise ValueError("Branch name cannot be empty.")

    @property
    def location(self) -> str:
        return self.__location

    @location.setter
    def location(self, new_location: str):
        if new_location and new_location.strip():
            self.__location = new_location.strip()
        else:
            raise ValueError("Location cannot be empty.")

    @property
    def working_hours(self) -> dict:
        return self.__working_hours.copy()

    @property
    def doctors(self) -> list:
        return self.__doctors.copy()

    # --- Business Logic Methods ---
    def set_working_hours(self, start_time: str, end_time: str) -> None:
        """
        Sets branch operational hours with strict format validation ('HH:MM').
        Ensures start time is earlier than end time.
        """
        try:
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
        except ValueError:
            raise ValueError("Invalid time format. Must be 'HH:MM'.")

        if start_dt >= end_dt:
            raise ValueError("Start time must be earlier than end time.")

        self.__working_hours["start"] = start_time
        self.__working_hours["end"] = end_time

    def add_service(self, service_name: str, duration_minutes: int, price: float) -> None:
        """
        Defines a medical service with duration and cost.
        Requirement: Kurumun sunduğu sağlık hizmetleri, süreleri ve ücret tanımlamaları.
        """
        if not service_name or not service_name.strip():
            raise ValueError("Service name cannot be empty.")
        if duration_minutes <= 0:
            raise ValueError("Duration must be a positive value (minutes).")
        if price < 0:
            raise ValueError("Price cannot be negative.")
        
        self.__services[service_name.strip()] = {
            "duration_minutes": duration_minutes,
            "price": round(float(price), 2)
        }

    def get_services(self) -> dict:
        """Returns all offered services in this branch."""
        return self.__services.copy()

    def assign_doctor(self, doctor_id: int) -> None:
        """Assigns a doctor to this branch."""
        if doctor_id not in self.__doctors:
            self.__doctors.append(doctor_id)

    def remove_doctor(self, doctor_id: int) -> bool:
        """Removes a doctor from this branch."""
        if doctor_id in self.__doctors:
            self.__doctors.remove(doctor_id)
            return True
        return False


def __str__(self) -> str:
        return (f"ClinicBranch [ID: {self.__branch_id}, Name: '{self.__name}', "
                f"Location: '{self.__location}', Services: {len(self.__services)}, "
                f"Doctors: {len(self.__doctors)}]")
