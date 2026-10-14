class MedicalService:
    """
    Represents a specific medical service offered by a clinic or hospital branch.
    Demonstrates Encapsulation by protecting pricing, duration, and status logic.
    """
    def __init__(self, service_id: int, name: str, duration_minutes: int, price: float, category: str = "General"):
        self.__service_id = service_id
        self.__name = name
        self.duration_minutes = duration_minutes  # Uses setter for validation
        self.price = price                      # Uses setter for validation
        self.__category = category
        self.__is_active = True                 # Service availability status

    # --- Properties (Getters & Setters) ---
    @property
    def service_id(self) -> int:
        return self.__service_id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, new_name: str):
        if new_name and new_name.strip():
            self.__name = new_name.strip()
        else:
            raise ValueError("Service name cannot be empty.")

    @property
    def duration_minutes(self) -> int:
        return self.__duration_minutes

    @duration_minutes.setter
    def duration_minutes(self, minutes: int):
        if isinstance(minutes, int) and minutes > 0:
            self.__duration_minutes = minutes
        else:
            raise ValueError("Duration must be a positive integer (minutes).")

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, amount: float):
        if isinstance(amount, (int, float)) and amount >= 0:
            self.__price = float(amount)
        else:
            raise ValueError("Price cannot be negative.")

    @property
    def category(self) -> str:
        return self.__category

    @property
    def is_active(self) -> bool:
        return self.__is_active

    # --- Business Logic Methods ---
    def deactivate_service((self) -> None:
        """Deactivates the medical service so it cannot be booked."""
        self.__is_active = False

    def activate_service(self) -> None:
        """Re-activates the medical service."""
        self.__is_active = True

    def apply_discount(self, percentage: float) -> None:
        """Applies a discount percentage to the service price."""
        if 0 < percentage <= 100:
            self.price = self.__price * (1 - (percentage / 100))
        else:
            raise ValueError("Discount percentage must be between 0 and 100.")

    def __str__(self) -> str:
        status = "Active" if self.__is_active else "Inactive"
        return f"Service [ID: {self.__service_id}, Name: '{self.__name}', Duration: {self.__duration_minutes} min, Price: {self.__price} TL, Status: {status}]"
