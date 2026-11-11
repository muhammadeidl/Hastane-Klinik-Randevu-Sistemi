
from datetime import datetime, timedelta, time
from decimal import Decimal

from app import uygulama_olustur

from modeller import (
    Hastane,
    Sube,
    Bolum,
    Hizmet,
    Hasta,
    Doktor,
    CalismaSaati
)

from servisler import (
    hizmet_ata,
    uygunluk_ekle,
    randevu_olustur,
    uygun_saatleri_getir
)

from veritabani import veritabani


def test_dolu_saat_listede_gorunmez():
    uygulama = uygulama_olustur({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test-anahtari"
    })

    with uygulama.app_context():
        hastane = Hastane(ad="Test Hastanesi")

        sube = Sube(
            ad="Merkez Sube",
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

        hasta = Hasta(
            ad="Ahmet",
            eposta="ahmet@test.com"
        )
        hasta.sifre_ayarla("GucluSifre123!")

        doktor = Doktor(
            ad="Dr. Mehmet",
            eposta="doktor@test.com",
            sube=sube
        )
        doktor.sifre_ayarla("GucluSifre123!")

        tarih = datetime.now().date() + timedelta(days=7)
        gun = tarih.weekday()

        calisma = CalismaSaati(
            gun=gun,
            baslangic=time(9, 0),
            bitis=time(17, 0),
            sube=sube
        )

        veritabani.session.add_all([
            hastane,
            sube,
            bolum,
            hizmet,
            hasta,
            doktor,
            calisma
        ])
        veritabani.session.commit()

        hizmet_ata(doktor, hizmet)

        uygunluk_ekle(
            doktor,
            gun,
            time(10, 0),
            time(12, 0)
        )

        veritabani.session.commit()

        saat_1000 = datetime.combine(
            tarih, time(10, 0)
        )

        saat_1030 = datetime.combine(
            tarih, time(10, 30)
        )

        # Ilk durumda iki saat de bos
        saatler = uygun_saatleri_getir(
            doktor, hizmet, tarih
        )

        assert saat_1000 in saatler
        assert saat_1030 in saatler

        # Saat 10:00 icin randevu olustur
        randevu_olustur(
            hasta,
            doktor,
            hizmet,
            saat_1000
        )

        veritabani.session.commit()

        # Tekrar uygun saatleri hesapla
        saatler = uygun_saatleri_getir(
            doktor, hizmet, tarih
        )

        # 10:00 artik dolu
        assert saat_1000 not in saatler

        # 10:30 hala uygun
        assert saat_1030 in saatler

        # Saatler sirali olmali
        assert saatler == sorted(saatler)
