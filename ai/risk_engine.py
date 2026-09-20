from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"


def _generate_synthetic_normal_data(n_samples: int = 1500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    records = []
    for _ in range(n_samples):
        login_hour = float(np.clip(rng.normal(14.0, 3.0), 0, 23))
        failed_attempts = int(max(0, rng.poisson(0.8)))
        recent_attempts = int(max(0, rng.poisson(2.4)))
        new_ip = bool(rng.random() < 0.08)
        new_device = bool(rng.random() < 0.05)
        time_since_previous_login = float(rng.uniform(0, 180.0))
        login_frequency = int(max(1, rng.poisson(3)))
        records.append(
            {
                "login_hour": login_hour,
                "failed_attempts": failed_attempts,
                "recent_attempts": recent_attempts,
                "new_ip": int(new_ip),
                "new_device": int(new_device),
                "time_since_previous_login": time_since_previous_login,
                "login_frequency": login_frequency,
            }
        )
    return pd.DataFrame(records)


def train_model(force: bool = False):
    if MODEL_PATH.exists() and not force:
        with MODEL_PATH.open("rb") as fh:
            return pickle.load(fh)

    training_data = _generate_synthetic_normal_data()
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
    )
    model.fit(training_data)

    with MODEL_PATH.open("wb") as fh:
        pickle.dump(model, fh)
    return model


def load_model():
    return train_model(force=False)


def train_model_if_needed(force: bool = False):
    return train_model(force=force)


def _feature_vector_from_attempt(login_features: dict) -> pd.DataFrame:
    feature_names = [
        "login_hour",
        "failed_attempts",
        "recent_attempts",
        "new_ip",
        "new_device",
        "time_since_previous_login",
        "login_frequency",
    ]
    return pd.DataFrame(
        [
            [
                float(login_features.get("login_hour", 12.0)),
                float(login_features.get("failed_attempts", 0)),
                float(login_features.get("recent_attempts", 0)),
                float(login_features.get("new_ip", 0)),
                float(login_features.get("new_device", 0)),
                float(login_features.get("time_since_previous_login", 0)),
                float(login_features.get("login_frequency", 1)),
            ]
        ],
        columns=feature_names,
    )


def assess_login_risk(login_features: dict):
    model = load_model()
    X = _feature_vector_from_attempt(login_features)
    decision = float(model.decision_function(X)[0])
    prediction = int(model.predict(X)[0])

    score = int(max(0, min(100, round((0.5 - decision) * 35))))

    if prediction == -1:
        score = max(score, 45)
    if login_features.get("new_ip"):
        score += 8
    if login_features.get("new_device"):
        score += 8
    if login_features.get("failed_attempts", 0) >= 3:
        score += 12
    if login_features.get("login_hour", 12.0) < 6 or login_features.get("login_hour", 12.0) > 22:
        score += 6
    if login_features.get("recent_attempts", 0) >= 5:
        score += 6
    if login_features.get("time_since_previous_login", 0) > 180:
        score += 5
    if login_features.get("login_frequency", 1) > 8:
        score += 4

    score = max(0, min(100, score))

    if score >= 70:
        risk_level = "HIGH"
        recommendation = "Block login and record security event"
    elif score >= 40:
        risk_level = "MEDIUM"
        recommendation = "Require MFA"
    else:
        risk_level = "LOW"
        recommendation = "Allow login"

    reasons = []
    if login_features.get("new_ip"):
        reasons.append("Login from a new IP address")
    if login_features.get("new_device"):
        reasons.append("New device or browser detected")
    if login_features.get("login_hour", 12.0) < 6 or login_features.get("login_hour", 12.0) > 22:
        reasons.append("Unusual login time")
    if login_features.get("failed_attempts", 0) >= 3:
        reasons.append("Repeated failed login attempts")
    if login_features.get("recent_attempts", 0) >= 5:
        reasons.append("Multiple recent login attempts")
    if login_features.get("time_since_previous_login", 0) > 180:
        reasons.append("Long gap since previous login")
    if not reasons:
        reasons.append("No major anomaly detected")

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
        "recommendation": recommendation,
        "model_prediction": int(prediction),
        "decision_score": round(decision, 4),
    }
