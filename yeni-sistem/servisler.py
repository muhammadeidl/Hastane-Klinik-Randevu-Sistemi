

from datetime import date, datetime, time, timedelta

from sqlalchemy import select

from modeller import (
    Hasta,
    Doktor,
    SaglikPersoneli,
    Yonetici,
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



def randevu_durum_degistir(randevu, kullanici, yeni_durum):
    if not isinstance(randevu, Randevu) or randevu.id is None:
        raise ValueError("Gecerli bir randevu gerekli")

    if kullanici is None or kullanici.id is None:
        raise ValueError("Kayitli kullanici gerekli")

    hasta_mi = (
        isinstance(kullanici, Hasta)
        and kullanici.id == randevu.hasta_id
    )

    calisan_mi = (
        isinstance(kullanici, (Doktor, SaglikPersoneli))
        and kullanici.id == randevu.calisan_id
    )

    yonetici_mi = False

    if isinstance(kullanici, Yonetici):
        yonetici_mi = (
            kullanici.hastane_id is not None
            and kullanici.hastane_id
            == randevu.hizmet.bolum.sube.hastane_id
        )

    if not (hasta_mi or calisan_mi or yonetici_mi):
        raise PermissionError("Bu randevu icin yetkiniz yok")

    if randevu.bitis <= datetime.now():
        raise ValueError("Gecmis randevu degistirilemez")

    izinli_gecisler = {
        "beklemede": ["onaylandi", "reddedildi", "iptal"],
        "onaylandi": ["iptal"],
        "reddedildi": [],
        "iptal": []
    }

    if yeni_durum not in izinli_gecisler.get(
        randevu.durum, []
    ):
        raise ValueError("Gecersiz durum degisikligi")

    if hasta_mi and not (calisan_mi or yonetici_mi):
        if yeni_durum != "iptal":
            raise PermissionError("Hasta sadece iptal edebilir")

    if yeni_durum in ("onaylandi", "reddedildi"):
        if not (calisan_mi or yonetici_mi):
            raise PermissionError("Onay veya ret yetkiniz yok")

    randevu.durum = yeni_durum
    return randevu



def uygun_saatleri_getir(calisan, hizmet, tarih):
    # 1. Girilen bilgileri kontrol et
    calisan_kontrol(calisan)

    if not isinstance(hizmet, Hizmet) or hizmet.id is None:
        raise ValueError("Gecerli bir hizmet gerekli")

    if not isinstance(tarih, date) or isinstance(tarih, datetime):
        raise ValueError("Gecerli bir tarih gerekli")

    if hizmet.sure_dakika <= 0:
        raise ValueError("Hizmet suresi gecersiz")

    # 2. Calisan bu hizmeti sunuyor mu?
    atama = veritabani.session.get(
        CalisanHizmet,
        (calisan.id, hizmet.id)
    )

    if atama is None:
        raise ValueError("Calisan bu hizmeti sunmuyor")

    if hizmet.bolum.sube_id != calisan.sube_id:
        raise ValueError("Hizmet farkli subeye ait")

    gun = tarih.weekday()

    # 3. Calisanin uygunluk saatleri
    uygunluklar = veritabani.session.scalars(
        select(CalisanUygunluk).where(
            CalisanUygunluk.calisan_id == calisan.id,
            CalisanUygunluk.gun == gun
        )
    ).all()

    # 4. Subenin calisma saatleri
    calisma_saatleri = veritabani.session.scalars(
        select(CalismaSaati).where(
            CalismaSaati.sube_id == calisan.sube_id,
            CalismaSaati.gun == gun
        )
    ).all()

    # 5. O gunun mevcut randevulari
    gun_baslangici = datetime.combine(tarih, time.min)
    gun_bitisi = gun_baslangici + timedelta(days=1)

    randevular = veritabani.session.scalars(
        select(Randevu).where(
            Randevu.calisan_id == calisan.id,
            Randevu.durum.in_(["beklemede", "onaylandi"]),
            Randevu.baslangic < gun_bitisi,
            Randevu.bitis > gun_baslangici
        )
    ).all()

    sure = timedelta(minutes=hizmet.sure_dakika)
    simdi = datetime.now()
    uygun_saatler = set()

    # 6. Uygun saatleri hesapla
    for uygunluk in uygunluklar:
        baslangic = datetime.combine(
            tarih, uygunluk.baslangic
        )

        uygunluk_bitisi = datetime.combine(
            tarih, uygunluk.bitis
        )

        while baslangic + sure <= uygunluk_bitisi:
            bitis = baslangic + sure

            # Gecmis bir saat olamaz
            gelecek_mi = baslangic > simdi

            # Sube bu saatte acik mi?
            sube_acik_mi = any(
                calisma.baslangic <= baslangic.time()
                and bitis.time() <= calisma.bitis
                and bitis.date() == tarih
                for calisma in calisma_saatleri
            )

            # Baska randevu ile cakisiyor mu?
            cakisma_var = any(
                baslangic < randevu.bitis
                and bitis > randevu.baslangic
                for randevu in randevular
            )

            if (
                gelecek_mi
                and sube_acik_mi
                and not cakisma_var
            ):
                uygun_saatler.add(baslangic)

            baslangic += sure

    return sorted(uygun_saatler)
