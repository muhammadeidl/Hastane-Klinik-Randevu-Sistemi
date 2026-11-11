
import os

from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from veritabani import veritabani


load_dotenv()


def uygulama_olustur(test_ayarlari=None):
    uygulama = Flask(__name__)

    # Veritabani ayarlari
    uygulama.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///randevu.db"
    )

    # Oturum ayarlari
    uygulama.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    uygulama.config["SESSION_COOKIE_HTTPONLY"] = True
    uygulama.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    if test_ayarlari:
        uygulama.config.update(test_ayarlari)

    if not uygulama.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY ayarlanmamis")

    veritabani.init_app(uygulama)

    import modeller
    from modeller import Hasta, Kullanici

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

        if not ad or len(ad) > 120:
            return render_template(
                "kayit.html",
                hata="Gecerli bir ad giriniz."
            ), 400

        if (
            not eposta
            or len(eposta) > 255
            or "@" not in eposta
        ):
            return render_template(
                "kayit.html",
                hata="Gecerli bir e-posta giriniz."
            ), 400

        if sifre != sifre_tekrar:
            return render_template(
                "kayit.html",
                hata="Sifreler eslesmiyor."
            ), 400

        if len(sifre) < 12:
            return render_template(
                "kayit.html",
                hata="Sifre en az 12 karakter olmali."
            ), 400

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

        hasta = Hasta(ad=ad, eposta=eposta)
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

        return redirect(url_for("ana_sayfa"))

    # Giris yapma
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

        if kullanici is None or not kullanici.sifre_kontrol(sifre):
            return render_template(
                "giris.html",
                hata="E-posta veya sifre hatali."
            ), 401

        # Eski oturum bilgilerini temizle
        session.clear()

        # Sadece kullanici kimligini sakla
        session["kullanici_id"] = kullanici.id

        return redirect(url_for("panel"))

    # Kullanici paneli
    @uygulama.route("/panel")
    def panel():
        kullanici_id = session.get("kullanici_id")

        if kullanici_id is None:
            return redirect(url_for("giris"))

        kullanici = veritabani.session.get(
            Kullanici,
            kullanici_id
        )

        if kullanici is None:
            session.clear()
            return redirect(url_for("giris"))

        return render_template(
            "panel.html",
            kullanici=kullanici
        )

    # Cikis yapma
    @uygulama.route("/cikis", methods=["POST"])
    def cikis():
        session.clear()
        return redirect(url_for("giris"))

    return uygulama


app = uygulama_olustur()


if __name__ == "__main__":
    app.run(debug=True)
