
import os

from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    g
)

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from veritabani import veritabani
from yetkiler import giris_gerekli, rol_gerekli


# .env dosyasindaki ayarlari yukle
load_dotenv()


def uygulama_olustur(test_ayarlari=None):
    # Flask uygulamasini olustur
    uygulama = Flask(__name__)

    # Veritabani ayarlari
    uygulama.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///randevu.db"
    )

    # Oturum ayarlari
    uygulama.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    uygulama.config["SESSION_COOKIE_HTTPONLY"] = True
    uygulama.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Test ayarlari varsa uygula
    if test_ayarlari:
        uygulama.config.update(test_ayarlari)

    # Gizli anahtar kontrolu
    if not uygulama.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY ayarlanmamis")

    # Veritabanini uygulamaya bagla
    veritabani.init_app(uygulama)

    # Modelleri yukle
    import modeller
    from modeller import Hasta, Kullanici

    # Veritabani tablolarini olustur
    with uygulama.app_context():
        veritabani.create_all()

    # Ana sayfa
    @uygulama.route("/")
    def ana_sayfa():
        return "Hastane Klinik Randevu Sistemi calisiyor!"

    # Hasta kayit sayfasi
    @uygulama.route("/kayit", methods=["GET", "POST"])
    def kayit():
        if request.method == "GET":
            return render_template("kayit.html")

        ad = request.form.get("ad", "").strip()
        eposta = request.form.get("eposta", "").strip().lower()
        sifre = request.form.get("sifre", "")
        sifre_tekrar = request.form.get("sifre_tekrar", "")

        # Ad kontrolu
        if not ad or len(ad) > 120:
            return render_template(
                "kayit.html",
                hata="Gecerli bir ad giriniz."
            ), 400

        # E-posta kontrolu
        if (
            not eposta
            or len(eposta) > 255
            or "@" not in eposta
        ):
            return render_template(
                "kayit.html",
                hata="Gecerli bir e-posta giriniz."
            ), 400

        # Sifre tekrar kontrolu
        if sifre != sifre_tekrar:
            return render_template(
                "kayit.html",
                hata="Sifreler eslesmiyor."
            ), 400

        # Sifre uzunlugu kontrolu
        if len(sifre) < 12:
            return render_template(
                "kayit.html",
                hata="Sifre en az 12 karakter olmali."
            ), 400

        # E-posta daha once kullanilmis mi?
        mevcut = veritabani.session.scalar(
            select(Kullanici).where(
                Kullanici.eposta == eposta
            )
        )

        if mevcut is not None:
            return render_template(
                "kayit.html",
                hata="Bu e-posta zaten kayitli."
            ), 409

        # Yeni hasta olustur
        hasta = Hasta(
            ad=ad,
            eposta=eposta
        )

        # Sifreyi guvenli sekilde ozetle
        hasta.sifre_ayarla(sifre)

        veritabani.session.add(hasta)

        try:
            veritabani.session.commit()

        except IntegrityError:
            veritabani.session.rollback()

            return render_template(
                "kayit.html",
                hata="Bu e-posta zaten kayitli."
            ), 409

        # Kayit basarili
        return redirect(url_for("ana_sayfa"))

    # Kullanici girisi
    @uygulama.route("/giris", methods=["GET", "POST"])
    def giris():
        if request.method == "GET":
            return render_template("giris.html")

        eposta = request.form.get("eposta", "").strip().lower()
        sifre = request.form.get("sifre", "")

        kullanici = veritabani.session.scalar(
            select(Kullanici).where(
                Kullanici.eposta == eposta
            )
        )

        # E-posta ve sifre kontrolu
        if kullanici is None or not kullanici.sifre_kontrol(sifre):
            return render_template(
                "giris.html",
                hata="E-posta veya sifre hatali."
            ), 401

        # Onceki oturum bilgilerini temizle
        session.clear()

        # Kullanici kimligini oturuma kaydet
        session["kullanici_id"] = kullanici.id

        return redirect(url_for("panel"))

    # Ortak kullanici paneli
    @uygulama.route("/panel")
    @giris_gerekli
    def panel():
        return render_template(
            "panel.html",
            kullanici=g.kullanici
        )

    # Sadece hastalar icin panel
    @uygulama.route("/hasta/panel")
    @rol_gerekli("hasta")
    def hasta_paneli():
        return render_template(
            "panel.html",
            kullanici=g.kullanici
        )

    # Doktor ve saglik personeli paneli
    @uygulama.route("/calisan/panel")
    @rol_gerekli("doktor", "saglik_personeli")
    def calisan_paneli():
        return render_template(
            "panel.html",
            kullanici=g.kullanici
        )

    # Hastane yoneticisi paneli
    @uygulama.route("/yonetici/panel")
    @rol_gerekli("yonetici")
    def yonetici_paneli():
        return render_template(
            "panel.html",
            kullanici=g.kullanici
        )

    # Kullanici cikisi
    @uygulama.route("/cikis", methods=["POST"])
    def cikis():
        session.clear()

        return redirect(url_for("giris"))

    return uygulama


# Uygulamayi olustur
app = uygulama_olustur()


# Gelistirme sunucusunu calistir
if __name__ == "__main__":
    app.run(debug=True)
