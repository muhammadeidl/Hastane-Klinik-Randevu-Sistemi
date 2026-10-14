class ClinicBranch:
    """
    Represents a Hospital or Clinic Branch in the system.
    Demonstrates Encapsulation by protecting internal service lists and operating hours.
    """
    def __init__(self, branch_id: int, name: str, location: str):
        self.__branch_id = branch_id
        self.__name = name
        self.__location = location
        self.__working_hours = {"start": "08:00", "end": "17:00"}
        self.__services = {}  # Stores medical services: {service_name: {"duration": int, "price": float}}
        self.__doctors = []    # Stores assigned doctor IDs or objects

    # --- Properties (Getters & Setters) ---
    @property
    def branch_id(self) -> int:
        return self.__branch_id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, new_name: str):
        if new_name.strip():
            self.__name = new_name
        else:
            raise ValueError("Branch name cannot be empty.")

    @property
    def working_hours(self) -> dict:
        return self.__working_hours.copy()

    # --- Business Logic Methods ---
    def set_working_hours(self, start_time: str, end_time: str) -> None:
        """Sets branch operational hours (e.g., '09:00', '18:00')."""
        self.__working_hours["start"] = start_time
        self.__working_hours["end"] = end_time

    def add_service(self, service_name: str, duration_minutes: int, price: float) -> None:
        """
        Defines a medical service with duration and cost.
        Requirement: Kurumun sunduğu sağlık hizmetleri, süreleri ve ücret tanımlamaları.
        """
        if duration_minutes <= 0 or price < 0:
            raise ValueError("Duration and price must be positive values.")
        
        self.__services[service_name] = {
            "duration_minutes": duration_minutes,
            "price": price
        }

    def get_services(self) -> dict:
        """Returns all offered services in this branch."""
        return self.__services.copy()

    def assign_doctor(self, doctor_id: int) -> None:
        """Assigns a doctor to this branch."""
        if doctor_id not in self.__doctors:
            self.__doctors.append(doctor_id)

    def __str__(self) -> str:
        return f"ClinicBranch(ID: {self.__branch_id}, Name: '{self.__name}', Services: {len(self.__services)})"
