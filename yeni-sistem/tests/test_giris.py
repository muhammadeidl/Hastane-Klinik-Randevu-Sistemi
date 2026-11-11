
import pytest

from app import uygulama_olustur
from modeller import Hasta
from veritabani import veritabani


@pytest.fixture
def istemci():
    uygulama = uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "sadece-test-icin-gizli-anahtar"
    })

    with uygulama.app_context():
        hasta = Hasta(
            ad="Ahmet Yilmaz",
            eposta="ahmet@test.com"
        )
        hasta.sifre_ayarla("GucluSifre123!")

        veritabani.session.add(hasta)
        veritabani.session.commit()

        yield uygulama.test_client()


def test_giris_sayfasi(istemci):
    cevap = istemci.get("/giris")

    assert cevap.status_code == 200
    assert b"Kullanici Girisi" in cevap.data


def test_basarili_giris(istemci):
    cevap = istemci.post("/giris", data={
        "eposta": "ahmet@test.com",
        "sifre": "GucluSifre123!"
    })

    assert cevap.status_code == 302
    assert "/hasta/panel" in cevap.location

    panel = istemci.get("/panel")

    assert panel.status_code == 200
    assert b"Ahmet Yilmaz" in panel.data


def test_hatali_sifre(istemci):
    cevap = istemci.post("/giris", data={
        "eposta": "ahmet@test.com",
        "sifre": "YanlisSifre123!"
    })

    assert cevap.status_code == 401


def test_giris_yapmadan_panel(istemci):
    cevap = istemci.get("/panel")

    assert cevap.status_code == 302
    assert "/giris" in cevap.location


def test_cikis(istemci):
    istemci.post("/giris", data={
        "eposta": "ahmet@test.com",
        "sifre": "GucluSifre123!"
    })

    cevap = istemci.post("/cikis")

    assert cevap.status_code == 302

    panel = istemci.get("/panel")

    assert panel.status_code == 302
    assert "/giris" in panel.location
