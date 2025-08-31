# src/nutrition.py
from typing import Dict

def estimate_calories(food_name: str, grams: float, kcal_per_100g: float):
    kcal = (kcal_per_100g * grams) / 100.0
    food = food_name.lower()
    if "salad" in food or "vegetable" in food or "apple" in food or "banana" in food:
        carbs_pct, protein_pct, fat_pct = 0.60, 0.10, 0.30
    elif "chicken" in food or "beef" in food or "steak" in food:
        carbs_pct, protein_pct, fat_pct = 0.10, 0.60, 0.30
    elif "ice cream" in food or "pizza" in food or "fries" in food or "burger" in food:
        carbs_pct, protein_pct, fat_pct = 0.40, 0.15, 0.45
    elif "coffee" in food:
        carbs_pct, protein_pct, fat_pct = 0.05, 0.05, 0.90
    else:
        carbs_pct, protein_pct, fat_pct = 0.45, 0.20, 0.35

    carbs_g = (kcal * carbs_pct) / 4.0
    protein_g = (kcal * protein_pct) / 4.0
    fat_g = (kcal * fat_pct) / 9.0
    return {
        "kcal": round(kcal, 1),
        "carbs_g": round(carbs_g, 1),
        "protein_g": round(protein_g, 1),
        "fat_g": round(fat_g, 1),
        "notes": f"Estimates based on heuristic for '{food_name}'."
    }
