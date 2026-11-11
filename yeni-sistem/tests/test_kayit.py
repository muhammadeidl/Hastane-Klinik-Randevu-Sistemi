
import pytest
from sqlalchemy import select

from app import uygulama_olustur
from modeller import Kullanici, Hasta
from veritabani import veritabani


@pytest.fixture
def uygulama():
    return uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://"
    })


def test_kayit_sayfasi(uygulama):
    cevap = uygulama.test_client().get("/kayit")

    assert cevap.status_code == 200
    assert b"Hasta Kayit Formu" in cevap.data


def test_hasta_kayit(uygulama):
    istemci = uygulama.test_client()

    cevap = istemci.post("/kayit", data={
        "ad": "Ahmet Yilmaz",
        "eposta": "AHMET@test.com",
        "sifre": "GucluSifre123!",
        "sifre_tekrar": "GucluSifre123!"
    })

    assert cevap.status_code == 302

    with uygulama.app_context():
        hasta = veritabani.session.scalar(
            select(Kullanici).where(
                Kullanici.eposta == "ahmet@test.com"
            )
        )

        assert isinstance(hasta, Hasta)
        assert hasta.sifre_kontrol("GucluSifre123!")


def test_tekrar_eposta_reddedilir(uygulama):
    istemci = uygulama.test_client()

    bilgiler = {
        "ad": "Ahmet",
        "eposta": "ahmet@test.com",
        "sifre": "GucluSifre123!",
        "sifre_tekrar": "GucluSifre123!"
    }

    ilk = istemci.post("/kayit", data=bilgiler)
    ikinci = istemci.post("/kayit", data=bilgiler)

    assert ilk.status_code == 302
    assert ikinci.status_code == 409


def test_kisa_sifre_reddedilir(uygulama):
    cevap = uygulama.test_client().post(
        "/kayit",
        data={
            "ad": "Ali",
            "eposta": "ali@test.com",
            "sifre": "123",
            "sifre_tekrar": "123"
        }
    )

    assert cevap.status_code == 400
