from flask import Flask


def uygulama_olustur():
    uygulama = Flask(__name__)

    @uygulama.route("/")
    def ana_sayfa():
        return "Hastane Klinik Randevu Sistemi calisiyor!"

    return uygulama


app = uygulama_olustur()


if __name__ == "__main__":
    app.run(debug=True)