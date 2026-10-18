from datetime import datetime

class Appointment:
    """
    Represents an appointment in the Hospital/Clinic system.
    Manages relationship between Patient, Doctor, and MedicalService, 
    along with approval and status workflow.
    """
    def __init__(self, appointment_id: int, patient, doctor, service, date_time: str):
        self.__appointment_id = appointment_id
        self.__patient = patient          # Patient object
        self.__doctor = doctor            # Doctor object
        self.__service = service          # MedicalService object
        self.__date_time = date_time      # Format: "YYYY-MM-DD HH:MM"
        self.__status = "Pending"         # Options: Pending, Approved, Cancelled, Completed
        self.__fee = service.price        # Inherits price from the selected medical service
