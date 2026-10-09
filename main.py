# =========================================================
#  Hastane / Klinik Randevu Sistemi
#  Temel Sınıf Yapıları (Base Classes)
# =========================================================

class User:
    """Tüm kullanıcılar için temel sınıf (Base Class)"""
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email

    def get_details(self):
        return f"ID: {self.user_id} | Ad: {self.name} | E-posta: {self.email}"


class Patient(User):
    """Hasta Sınıfı (User sınıfından türetilmiştir - Inheritance)"""
    def __init__(self, user_id, name, email, phone):
        super().__init__(user_id, name, email)
        self.phone = phone
        self.appointments = []

    def get_details(self):
        return f"[Hasta] {super().get_details()} | Tel: {self.phone}"


class Doctor(User):
    """Doktor Sınıfı (User sınıfından türetilmiştir)"""
    def __init__(self, user_id, name, email, specialty):
        super().__init__(user_id, name, email)
        self.specialty = specialty
        self.available_slots = []  # Uygun zaman dilimleri

    def get_details(self):
        return f"[Doktor] {super().get_details()} | Uzmanlık: {self.specialty}"


class Service:
    """Sağlık Hizmeti Sınıfı (Muayene, Laboratuvar vb.)"""
    def __init__(self, service_id, name, duration_minutes, price):
        self.service_id = service_id
        self.name = name
        self.duration_minutes = duration_minutes
        self.price = price

    def get_info(self):
        return f"Hizmet: {self.name} | Süre: {self.duration_minutes} dk | Ücret: {self.price} TL"


# --- Test / Başlangıç Kontrolü ---
if __name__ == "__main__":
    print("--- Hastane Randevu Sistemi Başlatıldı ---")
    
    # Örnek Nesne Oluşturma (Testing Objects)
    doc = Doctor(1, "Dr. Ahmet Yılmaz", "ahmet@hastane.com", "Kardiyoloji")
    pat = Patient(101, "Mehmet Kaya", "mehmet@gmail.com", "05551234567")
    srv = Service(1, "Genel Muayene", 30, 250)

    print(doc.get_details())
    print(pat.get_details())
    print(srv.get_info())
