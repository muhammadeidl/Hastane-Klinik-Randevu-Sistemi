
from datetime import time
from decimal import Decimal

from sqlalchemy import select

from app import app
from modeller import (
    Hastane,
    Sube,
    Bolum,
    Hizmet,
    Doktor,
    CalismaSaati,
    CalisanHizmet,
    CalisanUygunluk
)
from veritabani import veritabani


def baslangic_verileri_ekle():
    with app.app_context():
        mevcut = veritabani.session.scalar(
            select(Hastane).where(
                Hastane.ad == "Ornek Saglik Hastanesi"
            )
        )

        if mevcut is not None:
            print("Ornek hastane zaten mevcut.")
            return

        hastane = Hastane(
            ad="Ornek Saglik Hastanesi"
        )

        sube = Sube(
            ad="Kadikoy Sube",
            adres="Kadikoy, Istanbul",
            hastane=hastane
        )

        bolum = Bolum(
            ad="Kardiyoloji",
            sube=sube
        )

        hizmet = Hizmet(
            ad="Kardiyoloji Muayenesi",
            sure_dakika=30,
            ucret=Decimal("750.00"),
            bolum=bolum
        )

        doktor = Doktor(
            ad="Dr. Mehmet Yilmaz",
            eposta="doktor.demo@example.com",
            uzmanlik="Kardiyoloji",
            sube=sube
        )

        doktor.sifre_ayarla("DegistirBeni123!")

        veritabani.session.add_all([
            hastane, sube, bolum, hizmet, doktor
        ])
        veritabani.session.flush()

        for gun in range(5):
            calisma = CalismaSaati(
                gun=gun,
                baslangic=time(9, 0),
                bitis=time(17, 0),
                sube=sube
            )

            uygunluk = CalisanUygunluk(
                calisan_id=doktor.id,
                gun=gun,
                baslangic=time(10, 0),
                bitis=time(14, 0)
            )

            veritabani.session.add_all([
                calisma, uygunluk
            ])

        atama = CalisanHizmet(
            calisan_id=doktor.id,
            hizmet_id=hizmet.id
        )

        veritabani.session.add(atama)
        veritabani.session.commit()

        print("Ornek hastane ve doktor verileri eklendi.")


if __name__ == "__main__":
    baslangic_verileri_ekle()
