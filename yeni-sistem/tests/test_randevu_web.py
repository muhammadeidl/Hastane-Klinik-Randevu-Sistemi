
from datetime import datetime, timedelta, time
from decimal import Decimal

from app import uygulama_olustur
from modeller import (
    Hastane, Sube, Bolum, Hizmet,
    Hasta, Doktor, CalismaSaati
)
from servisler import hizmet_ata, uygunluk_ekle
from veritabani import veritabani


def test_web_randevu_olusturma():
    uygulama = uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test-anahtari"
    })

    with uygulama.app_context():
        hastane = Hastane(ad="Test Hastanesi")

        sube = Sube(
            ad="Test Sube",
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

        hasta = Hasta(
            ad="Ahmet",
            eposta="ahmet@test.com"
        )
        hasta.sifre_ayarla("GucluSifre123!")

        doktor = Doktor(
            ad="Mehmet",
            eposta="mehmet@test.com",
            sube=sube
        )
        doktor.sifre_ayarla("GucluSifre123!")

        tarih = datetime.now().date() + timedelta(days=7)
        gun = tarih.weekday()

        calisma = CalismaSaati(
            gun=gun,
            baslangic=time(9, 0),
            bitis=time(17, 0),
            sube=sube
        )

        veritabani.session.add_all([
            hastane, sube, bolum, hizmet,
            hasta, doktor, calisma
        ])
        veritabani.session.commit()

        hizmet_ata(doktor, hizmet)
        uygunluk_ekle(
            doktor, gun, time(10, 0), time(14, 0)
        )
        veritabani.session.commit()

        istemci = uygulama.test_client()

        # Giris yap
        istemci.post("/giris", data={
            "eposta": "ahmet@test.com",
            "sifre": "GucluSifre123!"
        })

        # Randevu sayfasini ac
        sayfa = istemci.get("/randevu/yeni")
        assert sayfa.status_code == 200

        # Yeni randevu olustur
        baslangic = datetime.combine(
            tarih, time(10, 0)
        )

        cevap = istemci.post("/randevu/yeni", data={
            "secim": f"{doktor.id}:{hizmet.id}",
            "tarih": baslangic.isoformat(timespec="minutes")
        })

        assert cevap.status_code == 302
        assert "/hasta/panel" in cevap.location

        # Randevunun panelde gorundugunu kontrol et
        panel = istemci.get("/hasta/panel")

        assert panel.status_code == 200
        assert b"Kalp Muayenesi" in panel.data
