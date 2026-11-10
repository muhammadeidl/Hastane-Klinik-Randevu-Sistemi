
from sqlalchemy import ForeignKey, String, Integer, Numeric, Time, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from datetime import time
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

    
class Bolum(veritabani.Model):
    __tablename__ = "bolumler"

    id: Mapped[int] = mapped_column(primary_key=True)

    ad: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    sube_id: Mapped[int] = mapped_column(
        ForeignKey("subeler.id"),
        nullable=False
    )

    sube: Mapped["Sube"] = relationship()

    def bilgi_goster(self):
        return f"Bolum: {self.ad}"


class Hizmet(veritabani.Model):
    __tablename__ = "hizmetler"

    __table_args__ = (
        CheckConstraint(
            "sure_dakika > 0",
            name="ck_hizmet_sure"
        ),
        CheckConstraint(
            "ucret >= 0",
            name="ck_hizmet_ucret"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    ad: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    sure_dakika: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    ucret: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    bolum_id: Mapped[int] = mapped_column(
        ForeignKey("bolumler.id"),
        nullable=False
    )

    bolum: Mapped["Bolum"] = relationship()

    def bilgi_goster(self):
        return f"{self.ad} - {self.sure_dakika} dakika"

class CalismaSaati(veritabani.Model):
    __tablename__ = "calisma_saatleri"

    __table_args__ = (
        UniqueConstraint(
            "sube_id",
            "gun",
            "baslangic",
            "bitis",
            name="uq_sube_calisma_saati"
        ),
        CheckConstraint(
            "gun BETWEEN 0 AND 6",
            name="ck_calisma_gun"
        ),
        CheckConstraint(
            "baslangic < bitis",
            name="ck_calisma_zaman"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    gun: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    baslangic: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    bitis: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    sube_id: Mapped[int] = mapped_column(
        ForeignKey("subeler.id"),
        nullable=False
    )

    sube: Mapped["Sube"] = relationship()