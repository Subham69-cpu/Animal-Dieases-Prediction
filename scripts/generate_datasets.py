"""
Generate sample hierarchical image folders (per project spec) and a flat folder layout for CNN training.
Also generates symptom_symptom_dataset.csv for ML models.
"""
import argparse
import csv
import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

# Nested layout (documentation / spec)
STRUCTURE = {
    "cow": ["mastitis", "foot_and_mouth", "black_quarter", "milk_fever"],
    "dog": ["rabies", "distemper", "skin_allergy", "parvovirus"],
    "cat": ["feline_flu", "ringworm", "skin_allergy", "distemper"],
    "goat": ["goat_pneumonia", "foot_rot", "foot_and_mouth", "mastitis"],
    "poultry": ["bird_flu", "newcastle", "fowl_pox"],
}

SYMPTOM_ROWS = []


def _tint_for(animal: str, disease: str) -> tuple:
    """Deterministic RGB tint for synthetic disease tiles."""
    rng = random.Random(f"{animal}:{disease}")
    base = [rng.randint(40, 180) for _ in range(3)]
    if "skin" in disease or "ringworm" in disease:
        base = [rng.randint(120, 220), rng.randint(80, 160), rng.randint(60, 140)]
    if "eye" in disease or "flu" in disease:
        base = [rng.randint(60, 120), rng.randint(140, 220), rng.randint(180, 255)]
    return tuple(base)


def make_tile(path: Path, animal: str, disease: str, size: int = 128):
    path.parent.mkdir(parents=True, exist_ok=True)
    tint = _tint_for(animal, disease)
    arr = np.random.randint(0, 40, (size, size, 3), dtype=np.uint8)
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + tint[c] // 3, 0, 255)
    # lesion-like blob
    img = Image.fromarray(arr)
    dr = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = random.Random(f"{animal}:{disease}:blob").randint(15, 35)
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 80, 80), width=3)
    img.save(path, quality=85)


def append_symptom_rows():
    """Build synthetic symptom -> disease mapping."""
    global SYMPTOM_ROWS
    SYMPTOM_ROWS = []
    for animal, diseases in STRUCTURE.items():
        for disease in diseases:
            for _ in range(25):
                row = {
                    "animal_type": animal,
                    "fever": random.randint(0, 1),
                    "cough": random.randint(0, 1),
                    "vomiting": random.randint(0, 1),
                    "diarrhea": random.randint(0, 1),
                    "skin_problem": random.randint(0, 1),
                    "breathing_issue": random.randint(0, 1),
                    "appetite_loss": random.randint(0, 1),
                    "weakness": random.randint(0, 1),
                    "disease": disease,
                }
                # bias symptoms weakly toward disease semantics
                r = random.Random(f"{animal}:{disease}:{row}")
                if "respiratory" in disease or "flu" in disease or "newcastle" in disease:
                    row["cough"] = max(row["cough"], r.choice([0, 1]))
                    row["breathing_issue"] = max(row["breathing_issue"], r.choice([0, 1]))
                if "skin" in disease or "ringworm" in disease or "fowl_pox" in disease:
                    row["skin_problem"] = 1
                if "foot" in disease or "parvo" in disease or "diarrhea" in disease:
                    row["diarrhea"] = max(row["diarrhea"], r.choice([0, 1]))
                if "mastitis" in disease or "milk" in disease:
                    row["fever"] = max(row["fever"], r.choice([0, 1]))
                SYMPTOM_ROWS.append(row)


def write_csv(root: Path):
    append_symptom_rows()
    csv_path = root / "symptom_dataset.csv"
    keys = [
        "animal_type",
        "fever",
        "cough",
        "vomiting",
        "diarrhea",
        "skin_problem",
        "breathing_issue",
        "appetite_loss",
        "weakness",
        "disease",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(SYMPTOM_ROWS)
    print(f"Wrote {csv_path} ({len(SYMPTOM_ROWS)} rows)")


def generate_images(root: Path, per_class: int, flat_root: Path):
    for animal, diseases in STRUCTURE.items():
        for disease in diseases:
            nested = root / animal / disease
            flat = flat_root / f"{animal}__{disease}"
            for i in range(per_class):
                make_tile(nested / f"img_{i:04d}.jpg", animal, disease)
                make_tile(flat / f"img_{i:04d}.jpg", animal, disease)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="Project root (default: parent of scripts/)")
    ap.add_argument("--per-class", type=int, default=40, help="Images per nested disease folder")
    args = ap.parse_args()
    root = Path(args.root or Path(__file__).resolve().parent.parent)
    dataset = root / "dataset"
    cnn_flat = root / "dataset" / "cnn_flat"
    dataset.mkdir(parents=True, exist_ok=True)
    cnn_flat.mkdir(parents=True, exist_ok=True)
    generate_images(dataset, args.per_class, cnn_flat)
    write_csv(dataset)
    print("Done. Nested:", dataset, "CNN flat:", cnn_flat)


if __name__ == "__main__":
    main()
