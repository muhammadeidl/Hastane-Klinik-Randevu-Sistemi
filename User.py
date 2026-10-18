class User:
    """
    Base class representing a generic user in the Hospital/Clinic system.
    Demonstrates Inheritance, Encapsulation, and Polymorphism.
    """
    def __init__(self, user_id: int, name: str, email: str, phone: str, role: str):
        self.__user_id = user_id
        self.__name = name
        self.__email = email
        self.__phone = phone
        self.__role = role

    # --- Properties (Getters & Setters) ---
    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, new_name: str):
        if new_name.strip():
            self.__name = new_name.strip()
        else:
            raise ValueError("Name cannot be empty.")

    @property
    def email(self) -> str:
        return self.__email

    @property
    def role(self) -> str:
        return self.__role

    # --- Polymorphic Method (Çok Biçimlilik) ---
    def get_dashboard_info(self) -> str:
        """
        Virtual method to be overridden by child classes.
        Demonstrates Polymorphism.
        """
        return f"User Profile: {self.__name} (Role: {self.__role})"

    def __str__(self) -> str:
        return f"User [ID: {self.__user_id}, Name: '{self.__name}', Role: {self.__role}]"
