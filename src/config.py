# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DB_PATH = os.getenv("DB_PATH", "./data/habits.db")
MODEL_DEVICE = os.getenv("MODEL_DEVICE", "cpu")  # "cpu" or "cuda"
