class Doctor:
    """
    Represents a Doctor or Health Personnel in the system.
    Manages specializations, branch association, and availability slots.
    """
    def __init__(self, doctor_id: int, name: str, specialization: str, branch_id: int):
        self.__doctor_id = doctor_id
        self.__name = name
        self.__specialization = specialization
        self.__branch_id = branch_id
        self.__services = []          # List of service IDs or names the doctor can perform
        self.__available_slots = []   # List of available time slots (e.g., ["10:00", "10:30", "11:00"])
        self.__is_active = True
        self.__is_close = True

    
    # --- Properties (Getters & Setters) ---
    @property
    def doctor_id(self) -> int:
        return self.__doctor_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def specialization(self) -> str:
        return self.__specialization

    @property
    def branch_id(self) -> int:
        return self.__branch_id

    @property
    def is_active(self) -> bool:
        return self.__is_active

    
    # --- Business Logic Methods ---
    def add_service(self, service_name: str) -> None:
        """Assigns a medical service that this doctor can perform."""
        if service_name not in self.__services:
            self.__services.append(service_name)

    def get_services(self) -> list:
        """Returns the list of services offered by this doctor."""
        return self.__services.copy()

    def add_available_slot(self, time_slot: str) -> None:
        """Adds an available time slot for appointments."""
        if time_slot not in self.__available_slots:
            self.__available_slots.append(time_slot)

    def remove_available_slot(self, time_slot: str) -> bool:
        """Removes a time slot (e.g., when booked)."""
        if time_slot in self.__available_slots:
            self.__available_slots.remove(time_slot)
            return True
        return False
