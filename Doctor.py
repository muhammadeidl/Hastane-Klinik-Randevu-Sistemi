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
