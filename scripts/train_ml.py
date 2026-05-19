"""Train RandomForest + XGBoost voting pipeline on dataset/symptom_dataset.csv."""
import json
import os
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)


def main():
    csv_path = ROOT / "dataset" / "symptom_dataset.csv"
    if not csv_path.is_file():
        print("Run: python scripts/generate_datasets.py first", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(csv_path)
    y = df["disease"]
    X = df.drop(columns=["disease"])

    sym_cols = [
        "fever",
        "cough",
        "vomiting",
        "diarrhea",
        "skin_problem",
        "breathing_issue",
        "appetite_loss",
        "weakness",
    ]
    pre = ColumnTransformer(
        [
            ("animal", OneHotEncoder(handle_unknown="ignore"), ["animal_type"]),
            ("sym", "passthrough", sym_cols),
        ]
    )
    rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
    xgb = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="mlogloss",
    )
    clf = VotingClassifier(estimators=[("rf", rf), ("xgb", xgb)], voting="soft")
    pipe = Pipeline([("prep", pre), ("clf", clf)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, pred)
    report = classification_report(y_test, pred)

    out = ROOT / "ml_model"
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, out / "symptom_pipeline.joblib")
    meta = {"accuracy": acc, "report": report}
    with open(out / "symptom_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Saved ml_model/symptom_pipeline.joblib accuracy:", round(acc, 4))
    print(report)


if __name__ == "__main__":
    main()
