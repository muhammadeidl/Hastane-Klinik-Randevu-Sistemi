
from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest

from app import uygulama_olustur
from modeller import (
    Hastane, Sube, Bolum, Hizmet,
    Hasta, Doktor, CalismaSaati, Randevu, Yonetici
)
from servisler import (
    hizmet_ata,
    uygunluk_ekle,
    randevu_olustur,
    randevu_durum_degistir
)
from veritabani import veritabani


@pytest.fixture
def veriler():
    uygulama = uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://"
    })

    with uygulama.app_context():
        hastane = Hastane(ad="Merkez Hastanesi")

        sube = Sube(
            ad="Kadikoy Sube",
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
            uzmanlik="Kardiyoloji",
            sube=sube
        )
        doktor.sifre_ayarla("GucluSifre123!")

        gun = (datetime.now() + timedelta(days=7)).weekday()

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

        tarih = datetime.combine(
            datetime.now().date() + timedelta(days=7),
            time(10, 0)
        )

        yield hasta, doktor, hizmet, tarih


def test_randevu_olusturma(veriler):
    hasta, doktor, hizmet, tarih = veriler

    randevu = randevu_olustur(
        hasta, doktor, hizmet, tarih
    )
    veritabani.session.commit()

    assert randevu.durum == "beklemede"
    assert randevu.sure_dakika == 30
    assert randevu.ucret == Decimal("750.00")
    assert randevu.bitis == tarih + timedelta(minutes=30)


def test_cakisan_randevu(veriler):
    hasta, doktor, hizmet, tarih = veriler

    randevu_olustur(hasta, doktor, hizmet, tarih)
    veritabani.session.commit()

    with pytest.raises(ValueError):
        randevu_olustur(
            hasta, doktor, hizmet,
            tarih + timedelta(minutes=15)
        )


def test_uygunluk_disinda_randevu(veriler):
    hasta, doktor, hizmet, tarih = veriler

    with pytest.raises(ValueError):
        randevu_olustur(
            hasta, doktor, hizmet,
            tarih.replace(hour=15)
        )


def test_ardisik_randevu(veriler):
    hasta, doktor, hizmet, tarih = veriler

    randevu_olustur(hasta, doktor, hizmet, tarih)
    veritabani.session.commit()

    ikinci = randevu_olustur(
        hasta, doktor, hizmet,
        tarih + timedelta(minutes=30)
    )
    veritabani.session.commit()

    assert ikinci.baslangic == tarih + timedelta(minutes=30)


def test_doktor_randevu_onaylama(veriler):
    hasta, doktor, hizmet, tarih = veriler

    randevu = randevu_olustur(
        hasta, doktor, hizmet, tarih
    )
    veritabani.session.commit()

    randevu_durum_degistir(
        randevu, doktor, "onaylandi"
    )
    veritabani.session.commit()

    assert randevu.durum == "onaylandi"


def test_hasta_randevu_iptal(veriler):
    hasta, doktor, hizmet, tarih = veriler

    randevu = randevu_olustur(
        hasta, doktor, hizmet, tarih
    )
    veritabani.session.commit()

    randevu_durum_degistir(
        randevu, hasta, "iptal"
    )
    veritabani.session.commit()

    assert randevu.durum == "iptal"


def test_hasta_randevu_onaylayamaz(veriler):
    hasta, doktor, hizmet, tarih = veriler

    randevu = randevu_olustur(
        hasta, doktor, hizmet, tarih
    )
    veritabani.session.commit()

    with pytest.raises(PermissionError):
        randevu_durum_degistir(
            randevu, hasta, "onaylandi"
        )

    assert randevu.durum == "beklemede"


def test_iptal_edilen_randevu_onaylanamaz(veriler):
    hasta, doktor, hizmet, tarih = veriler

    randevu = randevu_olustur(
        hasta, doktor, hizmet, tarih
    )
    veritabani.session.commit()

    randevu_durum_degistir(
        randevu, hasta, "iptal"
    )
    veritabani.session.commit()

    with pytest.raises(ValueError):
        randevu_durum_degistir(
            randevu, doktor, "onaylandi"
        )

    assert randevu.durum == "iptal"



def test_yonetici_randevu_onaylama(veriler):
    hasta, doktor, hizmet, tarih = veriler

    yonetici = Yonetici(
        ad="Hastane Yoneticisi",
        eposta="yonetici@test.com",
        hastane=hizmet.bolum.sube.hastane
    )
    yonetici.sifre_ayarla("GucluSifre123!")

    veritabani.session.add(yonetici)
    veritabani.session.commit()

    randevu = randevu_olustur(
        hasta, doktor, hizmet, tarih
    )
    veritabani.session.commit()

    randevu_durum_degistir(
        randevu, yonetici, "onaylandi"
    )
    veritabani.session.commit()

    assert randevu.durum == "onaylandi"


def test_farkli_hastane_yoneticisi_reddedilir(veriler):
    hasta, doktor, hizmet, tarih = veriler

    baska_hastane = Hastane(ad="Baska Hastane")

    yonetici = Yonetici(
        ad="Baska Yonetici",
        eposta="baska@test.com",
        hastane=baska_hastane
    )
    yonetici.sifre_ayarla("GucluSifre123!")

    veritabani.session.add(yonetici)
    veritabani.session.commit()

    randevu = randevu_olustur(
        hasta, doktor, hizmet, tarih
    )
    veritabani.session.commit()

    with pytest.raises(PermissionError):
        randevu_durum_degistir(
            randevu, yonetici, "onaylandi"
        )

    assert randevu.durum == "beklemede"
