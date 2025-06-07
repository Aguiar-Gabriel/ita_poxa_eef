from kedro.pipeline import Pipeline, node
from .nodes import load_data, train_model


def create_pipeline(**kwargs):
    return Pipeline([
        node(load_data, inputs="data", outputs="train_df", name="load_data"),
        node(train_model, inputs="train_df", outputs="model", name="train_catboost"),
    ])
