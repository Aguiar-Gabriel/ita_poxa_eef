import pandas as pd
from catboost import CatBoostRegressor


def load_data(data: pd.DataFrame) -> pd.DataFrame:
    """Pass-through node for loading data from the catalog."""
    return data


def train_model(df: pd.DataFrame) -> CatBoostRegressor:
    X = df.drop(columns=["target"])
    y = df["target"]
    model = CatBoostRegressor(iterations=10, verbose=False)
    model.fit(X, y)
    return model
