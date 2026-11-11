
from app import uygulama_olustur
from modeller import Hastane, Sube, Doktor
from veritabani import veritabani


def test_doktor_sube_iliskisi():
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

        doktor = Doktor(
            ad="Mehmet Yilmaz",
            eposta="mehmet@test.com",
            uzmanlik="Kardiyoloji",
            sube=sube
        )

        doktor.sifre_ayarla("GucluSifre123!")

        veritabani.session.add(doktor)
        veritabani.session.commit()

        assert doktor.sube.ad == "Kadikoy Sube"
        assert doktor.sube.hastane.ad == "Merkez Hastanesi"
        assert doktor.uzmanlik == "Kardiyoloji"
