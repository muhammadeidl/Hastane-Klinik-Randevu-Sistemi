
from datetime import time
from decimal import Decimal

import pytest
from sqlalchemy import select

from app import uygulama_olustur
from modeller import (
    Hastane, Sube, Bolum, Hizmet,
    Doktor, CalismaSaati,
    CalisanHizmet, CalisanUygunluk
)
from servisler import hizmet_ata, uygunluk_ekle
from veritabani import veritabani


@pytest.fixture
def test_verileri():
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

        doktor = Doktor(
            ad="Mehmet Yilmaz",
            eposta="mehmet@test.com",
            uzmanlik="Kardiyoloji",
            sube=sube
        )
        doktor.sifre_ayarla("GucluSifre123!")

        calisma = CalismaSaati(
            gun=0,
            baslangic=time(9, 0),
            bitis=time(17, 0),
            sube=sube
        )

        veritabani.session.add_all([
            hastane, sube, bolum,
            hizmet, doktor, calisma
        ])
        veritabani.session.commit()

        yield doktor, hizmet


def test_doktora_hizmet_atama(test_verileri):
    doktor, hizmet = test_verileri

    kayit = hizmet_ata(doktor, hizmet)
    veritabani.session.commit()

    assert kayit.calisan_id == doktor.id
    assert kayit.hizmet_id == hizmet.id

    with pytest.raises(ValueError):
        hizmet_ata(doktor, hizmet)


def test_uygunluk_ekleme(test_verileri):
    doktor, _ = test_verileri

    kayit = uygunluk_ekle(
        doktor, 0, time(10, 0), time(14, 0)
    )
    veritabani.session.commit()

    assert kayit.gun == 0
    assert kayit.baslangic == time(10, 0)

    kayitlar = veritabani.session.scalars(
        select(CalisanUygunluk)
    ).all()

    assert len(kayitlar) == 1


def test_cakisan_uygunluk(test_verileri):
    doktor, _ = test_verileri

    uygunluk_ekle(
        doktor, 0, time(10, 0), time(14, 0)
    )
    veritabani.session.commit()

    with pytest.raises(ValueError):
        uygunluk_ekle(
            doktor, 0, time(12, 0), time(15, 0)
        )


def test_sube_saati_disinda(test_verileri):
    doktor, _ = test_verileri

    with pytest.raises(ValueError):
        uygunluk_ekle(
            doktor, 0, time(7, 0), time(10, 0)
        )
