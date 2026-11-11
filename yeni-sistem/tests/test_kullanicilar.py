
from sqlalchemy import select

from app import uygulama_olustur
from modeller import (
    Kullanici, Hasta, Doktor,
    SaglikPersoneli, Yonetici
)
from veritabani import veritabani


def test_kullanici_rolleri():
    uygulama = uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://"
    })

    with uygulama.app_context():
        hasta = Hasta(
            ad="Ahmet",
            eposta="hasta@test.com"
        )

        doktor = Doktor(
            ad="Mehmet",
            eposta="doktor@test.com",
            uzmanlik="Kardiyoloji"
        )

        personel = SaglikPersoneli(
            ad="Ayse",
            eposta="personel@test.com"
        )

        yonetici = Yonetici(
            ad="Fatma",
            eposta="yonetici@test.com"
        )

        kullanicilar = [hasta, doktor, personel, yonetici]

        for kullanici in kullanicilar:
            kullanici.sifre_ayarla("GucluSifre123!")

        veritabani.session.add_all(kullanicilar)
        veritabani.session.commit()

        veritabani.session.expunge_all()

        kayitlar = veritabani.session.scalars(
            select(Kullanici)
        ).all()

        assert len(kayitlar) == 4

        assert any(
            isinstance(k, Hasta) for k in kayitlar
        )

        assert any(
            isinstance(k, Doktor) for k in kayitlar
        )

        assert any(
            isinstance(k, SaglikPersoneli) for k in kayitlar
        )

        assert any(
            isinstance(k, Yonetici) for k in kayitlar
        )

        assert doktor.rol_adi() == "Doktor"
        assert hasta.rol_adi() == "Hasta"


def test_sifre_guvenligi():
    uygulama = uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://"
    })

    with uygulama.app_context():
        hasta = Hasta(
            ad="Ali",
            eposta="ali@test.com"
        )

        hasta.sifre_ayarla("GucluSifre123!")

        assert hasta.sifre_kontrol("GucluSifre123!")
        assert not hasta.sifre_kontrol("YanlisSifre123!")

        assert hasta.sifre_ozeti != "GucluSifre123!"
