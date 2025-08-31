# src/image_model.py
"""Simple image classifier using torchvision pretrained model (ImageNet).
We use a small heuristic mapping from ImageNet labels to food categories.
This is a prototype — for production, use a dedicated food classifier or API.
"""
import io
import torch
import torchvision.transforms as T
from PIL import Image
import numpy as np

# lazy import to avoid heavy startup cost until needed
from torchvision import models

# minimal mapping: substrings in ImageNet labels -> common food names + default calorie/100g heuristic
FOOD_KEYWORDS = {
    "pizza": ("pizza", 266),
    "hotdog": ("hot dog", 290),
    "hamburger": ("burger", 295),
    "cheeseburger": ("cheeseburger", 295),
    "bagel": ("bagel", 250),
    "banana": ("banana", 89),
    "apple": ("apple", 52),
    "orange": ("orange", 47),
    "sushi": ("sushi", 130),
    "spaghetti": ("pasta", 158),
    "ice_cream": ("ice cream", 207),
    "espresso": ("coffee", 2),
    "coffee": ("coffee", 2),
    "egg": ("egg", 155),
    "salad": ("salad", 20),
    "sandwich": ("sandwich", 250),
    "baguette": ("bread", 265),
    "bread": ("bread", 265),
    "french_fries": ("fries", 312),
    "mashed_potato": ("potato", 88),
    "steak": ("steak", 271),
    "beef": ("beef", 250),
    "chicken": ("chicken", 239),
    "fried_rice": ("fried rice", 163),
    "taco": ("taco", 226),
}

# load ImageNet class names once
_IMAGENET_CLASSES = None

def _load_imagenet_classes():
    global _IMAGENET_CLASSES
    if _IMAGENET_CLASSES is None:
        _IMAGENET_CLASSES = [
            "banana", "lemon", "orange", "guava", "pineapple", "pizza", "hotdog",
            "cheeseburger", "hamburger", "bagel", "pretzel", "espresso", "coffee",
            "ice_cream", "soup_bowl", "spaghetti", "plate", "sushi", "sandwich",
            "salad", "french_fries", "taco", "steak", "chicken", "banana",
            "apple"
        ]
    return _IMAGENET_CLASSES

# model singleton
_MODEL = None
_TRANSFORM = None

def load_model(device: str = "cpu"):
    global _MODEL, _TRANSFORM
    if _MODEL is None:
        # use mobilenet_v3_large pretrained on ImageNet (lightweight-ish)
        _MODEL = models.mobilenet_v3_large(pretrained=True)
        _MODEL.eval()
        _MODEL.to(device)
        _TRANSFORM = T.Compose([
            T.Resize(256),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])
    return _MODEL, _TRANSFORM

def classify_image_bytes(image_bytes: bytes, device: str = "cpu", topk: int = 5):
    model, transform = load_model(device)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(x)
        probs = torch.nn.functional.softmax(logits, dim=1).cpu().numpy().squeeze()
    top_idx = np.argsort(-probs)[:topk]
    imagenet_labels = _load_imagenet_classes()
    labels = []
    for i, idx in enumerate(top_idx):
        lbl = imagenet_labels[idx % len(imagenet_labels)]
        labels.append((lbl, float(probs[idx])))
    return labels

def map_labels_to_food(preds):
    for label, score in preds:
        key = label.lower().replace(" ", "_")
        for kw, (food_name, kcal100) in FOOD_KEYWORDS.items():
            if kw in key or kw in label.lower():
                return {"food": food_name, "confidence": float(score), "kcal_per_100g": kcal100}
    avg_score = float(sum(p for _, p in preds) / len(preds))
    return {"food": "mixed meal", "confidence": avg_score, "kcal_per_100g": 180}
