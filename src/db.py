# src/db.py
import os
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime, Float, select, Text

DB_PATH = os.getenv("DB_PATH", "./data/habits.db")
os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
ENGINE = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
META = MetaData()

habits_table = Table(
    "habits", META,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

habit_logs = Table(
    "habit_logs", META,
    Column("id", Integer, primary_key=True),
    Column("habit_id", Integer),
    Column("timestamp", DateTime, default=datetime.utcnow),
    Column("note", Text, default=""),
)

meal_logs = Table(
    "meal_logs", META,
    Column("id", Integer, primary_key=True),
    Column("food", String),
    Column("grams", Float),
    Column("kcal", Float),
    Column("carbs_g", Float),
    Column("protein_g", Float),
    Column("fat_g", Float),
    Column("timestamp", DateTime, default=datetime.utcnow),
    Column("source", String, default="image_estimate"),
    Column("note", Text, default="")
)

def init_db():
    META.create_all(ENGINE)

def add_habit(name: str):
    with ENGINE.begin() as conn:
        conn.execute(habits_table.insert().values(name=name))
        return True

def list_habits():
    with ENGINE.connect() as conn:
        rows = conn.execute(select(habits_table)).fetchall()
        return [dict(r._mapping) for r in rows]

def log_habit(habit_id: int, note: str = ""):
    with ENGINE.begin() as conn:
        conn.execute(habit_logs.insert().values(habit_id=habit_id, note=note, timestamp=datetime.utcnow()))
        return True

def log_meal(food: str, grams: float, kcal: float, carbs_g: float, protein_g: float, fat_g: float, source: str="image_estimate", note: str=""):
    with ENGINE.begin() as conn:
        conn.execute(meal_logs.insert().values(
            food=food, grams=grams, kcal=kcal, carbs_g=carbs_g, protein_g=protein_g, fat_g=fat_g, timestamp=datetime.utcnow(), source=source, note=note
        ))
        return True

def recent_meals(limit: int = 20):
    with ENGINE.connect() as conn:
        rows = conn.execute(select(meal_logs).order_by(meal_logs.c.timestamp.desc()).limit(limit)).fetchall()
        return [dict(r._mapping) for r in rows]

def recent_habit_logs(limit: int = 50):
    with ENGINE.connect() as conn:
        rows = conn.execute(select(habit_logs).order_by(habit_logs.c.timestamp.desc()).limit(limit)).fetchall()
        return [dict(r._mapping) for r in rows]
