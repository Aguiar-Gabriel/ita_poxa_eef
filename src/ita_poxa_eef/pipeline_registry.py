from __future__ import annotations

from kedro.framework.project import pipelines
from kedro.pipeline import Pipeline
from .pipelines.catboost_model import create_pipeline as create_catboost_pipeline


def register_pipelines() -> dict[str, Pipeline]:
    catboost_pipeline = create_catboost_pipeline()
    return {
        "__default__": catboost_pipeline,
        "catboost": catboost_pipeline,
    }
