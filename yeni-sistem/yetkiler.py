
from functools import wraps

from flask import abort, g, redirect, session, url_for

from modeller import Kullanici
from veritabani import veritabani


def giris_gerekli(fonksiyon):
    @wraps(fonksiyon)
    def kontrol(*args, **kwargs):
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

        g.kullanici = kullanici

        return fonksiyon(*args, **kwargs)

    return kontrol


def rol_gerekli(*izinli_roller):
    def dekorator(fonksiyon):
        @wraps(fonksiyon)
        @giris_gerekli
        def kontrol(*args, **kwargs):
            if g.kullanici.rol not in izinli_roller:
                abort(403)

            return fonksiyon(*args, **kwargs)

        return kontrol

    return dekorator
