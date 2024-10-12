from settings import PG_DSN
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String

engine_async = create_async_engine(PG_DSN)
Session_async = async_sessionmaker(engine_async, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class SwapiPeople(Base):
    __tablename__ = "swapi_people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    birth_year: Mapped[str] = mapped_column(String(20), index=True)
    eye_color: Mapped[str] = mapped_column(String(20), index=True)
    films: Mapped[str] = mapped_column(String(250), index=True)
    gender: Mapped[str] = mapped_column(String(20), index=True)
    hair_color: Mapped[str] = mapped_column(String(20), index=True)
    height: Mapped[str] = mapped_column(String(20), index=True)
    homeworld: Mapped[str] = mapped_column(String(50), index=True)
    mass: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    skin_color: Mapped[str] = mapped_column(String(20), index=True)
    species: Mapped[str] = mapped_column(String(250), index=True)
    starships: Mapped[str] = mapped_column(String(250), index=True)
    vehicles: Mapped[str] = mapped_column(String(250), index=True)


async def migrate_orm():
    async with engine_async.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine_async.dispose()
