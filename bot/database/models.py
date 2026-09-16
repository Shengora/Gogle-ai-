import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Float, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")

    # Internal balances for Escrow off-chain
    balance_ton: Mapped[float] = mapped_column(Float, default=0.0)
    balance_stars: Mapped[int] = mapped_column(Integer, default=0)

    wallet_address: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    commission_percent: Mapped[float] = mapped_column(Float, default=5.0)


class Gift(Base):
    __tablename__ = "gifts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        BigInteger, index=True)  # References users.id or users.tg_id

    nft_address: Mapped[str] = mapped_column(
        String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    collection_address: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True)

    # Media and display attributes
    image_url: Mapped[Optional[str]] = mapped_column(
        String(1024), nullable=True)
    lottie_url: Mapped[Optional[str]] = mapped_column(
        String(1024), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    backdrop: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    symbol: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    gift_id: Mapped[int] = mapped_column(
        Integer, index=True)  # References gifts.id
    seller_id: Mapped[int] = mapped_column(BigInteger, index=True)

    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(
        String(10), default="TON")  # 'TON' or 'STARS'

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    buyer_id: Mapped[int] = mapped_column(BigInteger, index=True)
    seller_id: Mapped[int] = mapped_column(BigInteger, index=True)

    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10))
    commission_amount: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(
        String(20), default="completed")  # pending, completed, failed

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
