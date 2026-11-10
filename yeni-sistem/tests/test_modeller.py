
from app import uygulama_olustur
from modeller import Hastane, Sube
from veritabani import veritabani


def test_hastane_subeleri():
    uygulama = uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://"
    })

    with uygulama.app_context():
        hastane = Hastane(ad="Merkez Hastanesi")

        sube1 = Sube(
            ad="Merkez Sube",
            adres="Istanbul",
            hastane=hastane
        )

        sube2 = Sube(
            ad="Kadikoy Sube",
            adres="Kadikoy",
            hastane=hastane
        )

        veritabani.session.add_all([hastane, sube1, sube2])
        veritabani.session.commit()

        assert len(hastane.subeler) == 2
        assert sube1.hastane.ad == "Merkez Hastanesi"
