
from datetime import datetime, timedelta
from decimal import Decimal

from app import uygulama_olustur
from modeller import (
    Hasta, Doktor, Hastane, Sube,
    Bolum, Hizmet, Randevu
)
from veritabani import veritabani


def test_hasta_sadece_kendi_randevusunu_gorur():
    uygulama = uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "sadece-test-icin-gizli-anahtar"
    })

    with uygulama.app_context():
        hasta1 = Hasta(
            ad="Ahmet",
            eposta="ahmet@test.com"
        )
        hasta1.sifre_ayarla("GucluSifre123!")

        hasta2 = Hasta(
            ad="Ali",
            eposta="ali@test.com"
        )
        hasta2.sifre_ayarla("GucluSifre123!")

        hastane = Hastane(ad="Merkez Hastanesi")
        sube = Sube(
            ad="Merkez Sube",
            adres="Istanbul",
            hastane=hastane
        )

        bolum = Bolum(ad="Kardiyoloji", sube=sube)

        hizmet = Hizmet(
            ad="Kalp Muayenesi",
            sure_dakika=30,
            ucret=Decimal("750.00"),
            bolum=bolum
        )

        doktor = Doktor(
            ad="Mehmet",
            eposta="doktor@test.com",
            sube=sube
        )
        doktor.sifre_ayarla("GucluSifre123!")

        veritabani.session.add_all([
            hasta1, hasta2, hastane,
            sube, bolum, hizmet, doktor
        ])
        veritabani.session.commit()

        tarih = datetime.now() + timedelta(days=7)

        randevu = Randevu(
            hasta_id=hasta2.id,
            calisan_id=doktor.id,
            hizmet_id=hizmet.id,
            baslangic=tarih,
            bitis=tarih + timedelta(minutes=30),
            sure_dakika=30,
            ucret=Decimal("750.00"),
            durum="beklemede"
        )

        veritabani.session.add(randevu)
        veritabani.session.commit()

        istemci = uygulama.test_client()

        istemci.post("/giris", data={
            "eposta": "ahmet@test.com",
            "sifre": "GucluSifre123!"
        })

        cevap = istemci.get("/hasta/panel")

        assert cevap.status_code == 200
        assert b"Henuz randevunuz bulunmuyor." in cevap.data
        assert b"Kalp Muayenesi" not in cevap.data

        istemci.post("/cikis")

        istemci.post("/giris", data={
            "eposta": "ali@test.com",
            "sifre": "GucluSifre123!"
        })

        cevap = istemci.get("/hasta/panel")

        assert cevap.status_code == 200
        assert b"Kalp Muayenesi" in cevap.data
