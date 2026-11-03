"""First linear model: ridge regression on the feature list."""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from europapark_crowd.baselines import last_season_predictor, savvy_visitor_predictor
from europapark_crowd.evaluate import random_predictor, score
from europapark_crowd.features import add_features
from europapark_crowd.open_days import load_open_days
from europapark_crowd.windows import load_windows


def feature_columns(days: pd.DataFrame) -> pd.DataFrame:
    """Return only the columns the feature list adds to the open-day table."""
    return add_features(days).drop(columns=days.columns)


def linear_predictor(train: pd.DataFrame, target: pd.DataFrame) -> pd.Series:
    """Fit an untuned ridge model on the features and predict a crowd level per target day."""
    model = make_pipeline(
        ColumnTransformer(
            [("weekday", OneHotEncoder(), ["weekday"])], remainder="passthrough"
        ),
        Ridge(alpha=1.0),
    )
    model.fit(feature_columns(train), train["crowd_level"].astype(float))
    return pd.Series(model.predict(feature_columns(target)), index=target.index)


if __name__ == "__main__":
    days, windows = load_open_days(), load_windows()
    predictors = {
        "random": random_predictor,
        "savvy visitor": savvy_visitor_predictor,
        "last season": last_season_predictor,
        "linear": linear_predictor,
    }
    table = pd.concat(
        {name: score(predictor, days, windows) for name, predictor in predictors.items()},
        names=["model"],
    )
    print(table.round(3))
