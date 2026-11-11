

from datetime import datetime, time, timedelta

from sqlalchemy import select

from modeller import (
    Hasta,
    Doktor,
    SaglikPersoneli,
    Hizmet,
    Randevu,
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


def randevu_olustur(hasta, calisan, hizmet, baslangic):
    # 1. Kullanici ve tarih kontrolu
    if not isinstance(hasta, Hasta) or hasta.id is None:
        raise ValueError("Gecerli bir hasta gerekli")

    calisan_kontrol(calisan)

    if not isinstance(hizmet, Hizmet) or hizmet.id is None:
        raise ValueError("Gecerli bir hizmet gerekli")

    if not isinstance(baslangic, datetime):
        raise ValueError("Gecerli tarih ve saat gerekli")

    if baslangic.tzinfo is not None:
        raise ValueError("Yerel tarih ve saat kullanilmali")

    if baslangic <= datetime.now():
        raise ValueError("Gecmis bir tarihe randevu alinamaz")

    # 2. Hizmetin calisana atanmis olmasi
    atama = veritabani.session.get(
        CalisanHizmet,
        (calisan.id, hizmet.id)
    )

    if atama is None:
        raise ValueError("Calisan bu hizmeti sunmuyor")

    if hizmet.bolum.sube_id != calisan.sube_id:
        raise ValueError("Hizmet farkli subeye ait")

    # 3. Randevu bitis saatini hesapla
    if hizmet.sure_dakika <= 0:
        raise ValueError("Hizmet suresi gecersiz")

    bitis = baslangic + timedelta(
        minutes=hizmet.sure_dakika
    )

    # 4. Calisanin uygunluk kontrolu
    gun = baslangic.weekday()

    uygunluklar = veritabani.session.scalars(
        select(CalisanUygunluk).where(
            CalisanUygunluk.calisan_id == calisan.id,
            CalisanUygunluk.gun == gun
        )
    ).all()

    uygun = (
        bitis.date() == baslangic.date()
        and any(
            saat.baslangic <= baslangic.time()
            and bitis.time() <= saat.bitis
            for saat in uygunluklar
        )
    )

    if not uygun:
        raise ValueError("Calisan bu saatte uygun degil")

    # 5. Diger randevularla cakisma kontrolu
    cakisan = veritabani.session.scalar(
        select(Randevu).where(
            Randevu.calisan_id == calisan.id,
            Randevu.durum.in_(
                ["beklemede", "onaylandi"]
            ),
            Randevu.baslangic < bitis,
            Randevu.bitis > baslangic
        )
    )

    if cakisan is not None:
        raise ValueError("Bu saatte baska randevu var")

    # 6. Randevuyu olustur
    randevu = Randevu(
        hasta_id=hasta.id,
        calisan_id=calisan.id,
        hizmet_id=hizmet.id,
        baslangic=baslangic,
        bitis=bitis,
        sure_dakika=hizmet.sure_dakika,
        ucret=hizmet.ucret,
        durum="beklemede"
    )

    veritabani.session.add(randevu)

    return randevu
