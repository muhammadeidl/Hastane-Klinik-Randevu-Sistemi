from datetime import datetime

class Appointment:
    """
    Represents an appointment in the Hospital/Clinic system.
    Manages relationship between Patient, Doctor, and MedicalService, 
    along with approval, status workflow, and strict data validation.
    """
    def __init__(self, appointment_id: int, patient, doctor, service, date_time: str):
        self.__appointment_id = appointment_id
        self.__patient = patient          # Patient object
        self.__doctor = doctor            # Doctor object
        self.__service = service          # MedicalService object
        self.date_time = date_time        # Uses setter for format validation
        self.__status = "Pending"         # Options: Pending, Approved, Cancelled, Completed
        self.__fee = float(service.price) # Inherits price from the selected medical service

    # --- Properties (Getters & Setters) ---
    @property
    def appointment_id(self) -> int:
        return self.__appointment_id

    @property
    def patient(self):
        return self.__patient

    @property
    def doctor(self):
        return self.__doctor

    @property
    def service(self):
        return self.__service

    @property
    def date_time(self) -> str:
        return self.__date_time

    @date_time.setter
    def date_time(self, new_date_time: str):
        """Validates and sets the appointment date/time format ('YYYY-MM-DD HH:MM')."""
        try:
            datetime.strptime(new_date_time, "%Y-%m-%d %H:%M")
            self.__date_time = new_date_time
        except ValueError:
            raise ValueError("Invalid date_time format. Must be 'YYYY-MM-DD HH:MM'.")

    @property
    def status(self) -> str:
        return self.__status

    @property
    def fee(self) -> float:
        return self.__fee

    # --- Business Logic Methods ---
    def approve_appointment(self) -> None:
        """Approves the appointment (Requirement: Onay mekanizması)."""
        self.__status = "Approved"

    def cancel_appointment(self) -> None:
        """Cancels the appointment."""
        self.__status = "Cancelled"

    def complete_appointment(self) -> None:
        """Marks the appointment as completed after visit."""
        self.__status = "Completed"

    def __str__(self) -> str:
        return (f"Appointment [ID: {self.__appointment_id}] | "
                f"Patient: {self.__patient.name} | "
                f"Doctor: Dr. {self.__doctor.name} | "
                f"Service: {self.__service.name} | "
                f"Time: {self.__date_time} | "
                f"Status: {self.__status} | "
                f"Fee: {self.__fee} TL")

