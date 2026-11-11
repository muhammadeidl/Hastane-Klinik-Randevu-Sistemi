
from sqlalchemy import inspect, text

from app import app
from veritabani import veritabani


with app.app_context():
    kontrol = inspect(veritabani.engine)

    sutunlar = {
        sutun["name"]
        for sutun in kontrol.get_columns("kullanicilar")
    }

    if "hastane_id" not in sutunlar:
        veritabani.session.execute(
            text(
                "ALTER TABLE kullanicilar "
                "ADD COLUMN hastane_id INTEGER "
                "REFERENCES hastaneler(id)"
            )
        )
        veritabani.session.commit()
        print("hastane_id sutunu eklendi.")
    else:
        print("hastane_id zaten mevcut.")
