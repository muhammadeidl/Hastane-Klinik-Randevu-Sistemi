
from flask import Flask

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

    with uygulama.app_context():
        veritabani.create_all()

    @uygulama.route("/")
    def ana_sayfa():
        return "Hastane Klinik Randevu Sistemi calisiyor!"

    return uygulama


app = uygulama_olustur()


if __name__ == "__main__":
    app.run(debug=True)
