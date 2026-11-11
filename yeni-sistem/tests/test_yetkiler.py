
import pytest

from app import uygulama_olustur
from modeller import Hasta, Doktor, Yonetici
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
            ad="Ahmet",
            eposta="hasta@test.com"
        )

        doktor = Doktor(
            ad="Mehmet",
            eposta="doktor@test.com"
        )

        yonetici = Yonetici(
            ad="Ayse",
            eposta="yonetici@test.com"
        )

        for kullanici in [hasta, doktor, yonetici]:
            kullanici.sifre_ayarla("GucluSifre123!")

        veritabani.session.add_all([
            hasta, doktor, yonetici
        ])
        veritabani.session.commit()

        yield uygulama.test_client()


def giris_yap(istemci, eposta):
    return istemci.post("/giris", data={
        "eposta": eposta,
        "sifre": "GucluSifre123!"
    })


def test_misafir_panel_acamaz(istemci):
    cevap = istemci.get("/hasta/panel")

    assert cevap.status_code == 302
    assert "/giris" in cevap.location


def test_hasta_kendi_paneline_girer(istemci):
    giris_yap(istemci, "hasta@test.com")

    cevap = istemci.get("/hasta/panel")

    assert cevap.status_code == 200
    assert b"Ahmet" in cevap.data


def test_hasta_yonetici_paneline_giremez(istemci):
    giris_yap(istemci, "hasta@test.com")

    cevap = istemci.get("/yonetici/panel")

    assert cevap.status_code == 403


def test_doktor_calisan_paneline_girer(istemci):
    giris_yap(istemci, "doktor@test.com")

    cevap = istemci.get("/calisan/panel")

    assert cevap.status_code == 200


def test_doktor_yonetici_paneline_giremez(istemci):
    giris_yap(istemci, "doktor@test.com")

    cevap = istemci.get("/yonetici/panel")

    assert cevap.status_code == 403


def test_yonetici_yonetici_paneline_girer(istemci):
    giris_yap(istemci, "yonetici@test.com")

    cevap = istemci.get("/yonetici/panel")

    assert cevap.status_code == 200


def test_cikis_sonrasi_panel_kapanir(istemci):
    giris_yap(istemci, "hasta@test.com")

    istemci.post("/cikis")

    cevap = istemci.get("/hasta/panel")

    assert cevap.status_code == 302
    assert "/giris" in cevap.location
