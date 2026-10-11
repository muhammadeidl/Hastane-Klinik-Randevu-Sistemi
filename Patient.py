class Patient:
    """
    Represents a patient within the Hospital/Clinic Appointment System.
    Demonstrates Encapsulation by protecting personal attributes.
    """
    def __init__(self, patient_id: str, name: str, phone: str, email: str):
        # Private attributes (Encapsulation)
        self.__patient_id = patient_id
        self.__name = name
        self.__phone = phone
        self.__email = email
        self.__appointments = []  # Stores history of appointments

    # --- Getters and Setters (Properties) ---
    
    @property
    def patient_id(self) -> str:
        return self.__patient_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def phone(self) -> str:
        return self.__phone

    @phone.setter
    def phone(self, new_phone: str):
        if len(new_phone) >= 10:  # Simple validation logic
            self.__phone = new_phone
        else:
            raise ValueError("Invalid phone number length.")

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, new_email: str):
        if "@" in new_email:
            self.__email = new_email
        else:
            raise ValueError("Invalid email address.")

   
