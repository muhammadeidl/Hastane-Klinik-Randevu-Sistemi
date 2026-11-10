
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from veritabani import veritabani


class Hastane(veritabani.Model):
    __tablename__ = "hastaneler"

    id: Mapped[int] = mapped_column(primary_key=True)

    ad: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    subeler: Mapped[list["Sube"]] = relationship(
        back_populates="hastane"
    )

    def bilgi_goster(self):
        return f"Hastane: {self.ad}"


class Sube(veritabani.Model):
    __tablename__ = "subeler"

    id: Mapped[int] = mapped_column(primary_key=True)

    ad: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    adres: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    hastane_id: Mapped[int] = mapped_column(
        ForeignKey("hastaneler.id"),
        nullable=False
    )

    hastane: Mapped["Hastane"] = relationship(
        back_populates="subeler"
    )

    def bilgi_goster(self):
        return f"Sube: {self.ad}"
