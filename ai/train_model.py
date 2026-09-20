from ai.risk_engine import train_model_if_needed


if __name__ == "__main__":
    model = train_model_if_needed(force=True)
    print(f"Model trained successfully: {model.__class__.__name__}")
