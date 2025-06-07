# ita_poxa_eef

Exemplo de projeto com uma pipeline Kedro que utiliza CatBoost. O dataset de entrada fica em `data/01_raw/data.csv` e o modelo treinado é salvo em `data/06_models/model.pkl`.

Para executar a pipeline:

```bash
kedro run --pipeline catboost
```
