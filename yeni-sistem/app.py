
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from veritabani import veritabani


def uygulama_olustur(test_ayarlari=None):
    uygulama = Flask(__name__)

    uygulama.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///randevu.db"
    )

    if test_ayarlari:
        uygulama.config.update(test_ayarlari)

    veritabani.init_app(uygulama)

    import modeller
    from modeller import Hasta, Kullanici

    with uygulama.app_context():
        veritabani.create_all()

    @uygulama.route("/")
    def ana_sayfa():
        return "Hastane Klinik Randevu Sistemi calisiyor!"

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

    return uygulama


app = uygulama_olustur()


if __name__ == "__main__":
    app.run(debug=True)
