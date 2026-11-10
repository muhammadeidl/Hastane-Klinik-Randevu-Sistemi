
from datetime import time
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app import uygulama_olustur
from modeller import Hastane, Sube, Bolum, Hizmet, CalismaSaati
from veritabani import veritabani


@pytest.fixture
def uygulama():
    return uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://"
    })


def test_bolum_ve_hizmet(uygulama):
    with uygulama.app_context():
        hastane = Hastane(ad="Merkez Hastanesi")

        sube = Sube(
            ad="Kadikoy Sube",
            adres="Istanbul",
            hastane=hastane
        )

        bolum = Bolum(
            ad="Kardiyoloji",
            sube=sube
        )

        hizmet = Hizmet(
            ad="Kalp Muayenesi",
            sure_dakika=30,
            ucret=Decimal("750.00"),
            bolum=bolum
        )

        veritabani.session.add(hizmet)
        veritabani.session.commit()

        assert hizmet.bolum.ad == "Kardiyoloji"
        assert bolum.sube.ad == "Kadikoy Sube"
        assert hizmet.sure_dakika == 30
        assert hizmet.ucret == Decimal("750.00")


def test_calisma_saati(uygulama):
    with uygulama.app_context():
        hastane = Hastane(ad="Merkez Hastanesi")

        sube = Sube(
            ad="Merkez Sube",
            adres="Istanbul",
            hastane=hastane
        )

        saat = CalismaSaati(
            gun=0,
            baslangic=time(9, 0),
            bitis=time(17, 0),
            sube=sube
        )

        veritabani.session.add(saat)
        veritabani.session.commit()

        assert saat.gun == 0
        assert saat.baslangic == time(9, 0)
        assert saat.bitis == time(17, 0)


def test_gecersiz_hizmet_suresi(uygulama):
    with uygulama.app_context():
        hastane = Hastane(ad="Test Hastanesi")
        sube = Sube(
            ad="Test Sube",
            adres="Istanbul",
            hastane=hastane
        )
        bolum = Bolum(ad="Test Bolum", sube=sube)

        hizmet = Hizmet(
            ad="Hatali Hizmet",
            sure_dakika=-15,
            ucret=Decimal("100.00"),
            bolum=bolum
        )

        veritabani.session.add(hizmet)

        with pytest.raises(IntegrityError):
            veritabani.session.commit()

        veritabani.session.rollback()
