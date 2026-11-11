
from datetime import time

from sqlalchemy import select

from modeller import (
    Doktor,
    SaglikPersoneli,
    CalismaSaati,
    CalisanHizmet,
    CalisanUygunluk
)
from veritabani import veritabani


def calisan_kontrol(calisan):
    if not isinstance(calisan, (Doktor, SaglikPersoneli)):
        raise ValueError("Gecerli bir calisan gerekli")

    if calisan.id is None or calisan.sube_id is None:
        raise ValueError("Calisan subeye kayitli olmali")


def hizmet_ata(calisan, hizmet):
    calisan_kontrol(calisan)

    if hizmet.id is None:
        raise ValueError("Hizmet kayitli olmali")

    if hizmet.bolum.sube_id != calisan.sube_id:
        raise ValueError("Hizmet farkli bir subeye ait")

    mevcut = veritabani.session.get(
        CalisanHizmet,
        (calisan.id, hizmet.id)
    )

    if mevcut is not None:
        raise ValueError("Hizmet zaten atanmis")

    kayit = CalisanHizmet(
        calisan_id=calisan.id,
        hizmet_id=hizmet.id
    )

    veritabani.session.add(kayit)
    return kayit


def uygunluk_ekle(calisan, gun, baslangic, bitis):
    calisan_kontrol(calisan)

    if not isinstance(gun, int) or not 0 <= gun <= 6:
        raise ValueError("Gecersiz gun")

    if not isinstance(baslangic, time) or not isinstance(bitis, time):
        raise ValueError("Saat bilgisi hatali")

    if baslangic >= bitis:
        raise ValueError("Baslangic bitisten once olmali")

    # Subenin o gunku calisma saatleri
    calisma_saatleri = veritabani.session.scalars(
        select(CalismaSaati).where(
            CalismaSaati.sube_id == calisan.sube_id,
            CalismaSaati.gun == gun
        )
    ).all()

    uygun = any(
        saat.baslangic <= baslangic
        and bitis <= saat.bitis
        for saat in calisma_saatleri
    )

    if not uygun:
        raise ValueError("Sube calisma saatleri disinda")

    # Calisanin mevcut uygunluk saatleri
    mevcut_saatler = veritabani.session.scalars(
        select(CalisanUygunluk).where(
            CalisanUygunluk.calisan_id == calisan.id,
            CalisanUygunluk.gun == gun
        )
    ).all()

    for mevcut in mevcut_saatler:
        if baslangic < mevcut.bitis and mevcut.baslangic < bitis:
            raise ValueError("Uygunluk saatleri cakisiyor")

    kayit = CalisanUygunluk(
        calisan_id=calisan.id,
        gun=gun,
        baslangic=baslangic,
        bitis=bitis
    )

    veritabani.session.add(kayit)
    return kayit
