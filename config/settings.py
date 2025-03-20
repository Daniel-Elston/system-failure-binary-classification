from __future__ import annotations

import logging
from pprint import pformat

import attr
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# from config.factory import Factory


class Factory:
    def __init__(self):
        attr_dict = attr.asdict(self)
        logging.debug(f"Factory:\n{pformat(attr_dict)}\n")

    @staticmethod
    def create_sampler(sampling_type: str, sampling_params: dict):
        """Creates and returns an instance of the requested sampler."""
        samplers = {
            "smote": SMOTE,
            "undersampling": RandomUnderSampler,
        }
        if sampling_type not in samplers:
            raise ValueError(f"Unknown sampling technique: {sampling_type}")
        return samplers[sampling_type](**sampling_params)

    @staticmethod
    def create_model(
        model_type: str,
        model_params: dict
    ):
        """Creates and returns an instance of the requested model."""
        models = {
            "xgb": XGBClassifier,
            "lgbm": LGBMClassifier,
            "rf": RandomForestClassifier,
        }
        if model_type not in models:
            raise ValueError(f"Unsupported model type: {model_type}. Add to Factory.")
        return models[model_type](**model_params)


def col_types():
    return {
        "categorical_cols": [
            'loc',
            'target'
        ],
        "numeric_info_cols": [
            'comp_age',
            'monthly_run_time',
            'flow_rate',
            'days_since_maintenance',
            # 'opx_vol',
            'max_output_rate',
            # 'target'
        ],
        'sensor_cols': [
            's1',
            's2',
            's3',
            's4',
            's5',
            's6',
        ],
    }


@attr.s
class Config:
    random_state: int = attr.ib(default=42)

    # Output settings
    write_output: bool = attr.ib(default=True)
    overwrite: bool = attr.ib(default=True)
    save_fig: bool = attr.ib(default=True)
    show_fig: bool = attr.ib(default=False)

    # Data settings
    target_col: str = attr.ib(default='target')
    col_types: dict = attr.ib(factory=col_types)

    # Feature Engineering & Data Processing
    log_skew_threshold: float = attr.ib(default=1)
    kurtosis_threshold: float = attr.ib(default=3)
    boxcox_skew_threshold: float = attr.ib(default=1.5)
    yeo_johnson_skew_threshold: float = attr.ib(default=1.5)
    iqr_upper: float = attr.ib(default=0.01)
    iqr_lower: float = attr.ib(default=0.99)

    # def __attrs_post_init__(self):
    #     attr_dict = attr.asdict(self)
    #     logging.debug(f"{self.__class__.__name__}:\n{pformat(attr_dict)}\n")


@attr.s
class Params:
    model_type: str = attr.ib(default='xgb')
    target_sample_technique: str = attr.ib(default='smote')

    sampling_params: dict = attr.ib(default={
        "random_state": 42
    })
    model_params: dict = attr.ib(default={
        "random_state": 42,
        "eval_metric": "logloss"
    })

    def get_model(self):
        """Uses ModelFactory to instantiate the model dynamically."""
        return Factory.create_model(self.model_type, self.model_params)

    def get_sampler(self):
        """Uses SamplerFactory to instantiate the sampler dynamically."""
        return Factory.create_sampler(self.target_sample_technique, self.sampling_params)

    # def __attrs_post_init__(self):
    #     attr_dict = attr.asdict(self)
    #     logging.debug(f"{self.__class__.__name__}:\n{pformat(attr_dict)}\n")


@attr.s
class HyperParams:
    test_size: float = attr.ib(default=0.25)
    cv_folds: int = attr.ib(default=2)
    remove_outliers: bool = attr.ib(default=False)

    param_dist: dict = attr.ib(default={
        'classifier__n_estimators': [100, 200, 300],
        'classifier__max_depth': [3, 5, 7, 9],
        'classifier__learning_rate': [0.01, 0.05, 0.1],
        'classifier__subsample': [0.6, 0.8, 1.0],
        'classifier__colsample_bytree': [0.6, 0.8, 1.0],
        'classifier__scale_pos_weight': [1, 3, 5, 7]
    })

    # def __attrs_post_init__(self):
    #     attr_dict = attr.asdict(self)
    #     logging.debug(f"{self.__class__.__name__}:\n{pformat(attr_dict)}\n")


@attr.s
class Settings:
    """config, params, hyper_params"""
    config: Config = attr.ib(factory=Config)
    params: Params = attr.ib(factory=Params)
    hyperparams: HyperParams = attr.ib(factory=HyperParams)

    def __attrs_post_init__(self):
        attr_dict = attr.asdict(self)
        logging.debug(f"{self.__class__.__name__}:\n{pformat(attr_dict)}\n")


# @attr.s
# class Config:
#     write_output: bool = attr.ib(default=True)
#     overwrite: bool = attr.ib(default=True)
#     save_fig: bool = attr.ib(default=True)

#     def __attrs_post_init__(self):
#         attr_dict = attr.asdict(self)
#         logging.debug(f"DataConfig:\n{pformat(attr_dict)}\n")


# @attr.s
# class Params:
#     chunk_size: int = attr.ib(default=1000)
#     chunk_overlap: int = attr.ib(default=50)
#     truncation: bool = attr.ib(default=True)
#     max_input_seq_length: int = attr.ib(default=512)
#     max_output_seq_length: int = attr.ib(default=512)
#     separators: list = attr.ib(
#         default=["\n\n", "\n", ".", ";", ",", " ", ""]
#     )
#     embedding_model_name: str = attr.ib(
#         default="sentence-transformers/all-MiniLM-L6-v2"
#     )
#     language_model_name: str = attr.ib(
#         default="google/flan-t5-base"
#     )

#     def __attrs_post_init__(self):
#         attr_dict = attr.asdict(self)
#         logging.debug(f"ModelConfig:\n{pformat(attr_dict)}\n")


# @attr.s
# class HyperParams:
#     pass

#     def __attrs_post_init__(self):
#         # attr_dict = attr.asdict(self)
#         # logging.debug(f"ModelConfig:\n{pformat(attr_dict)}\n")
#         pass


# @attr.s
# class Settings:
#     """config, params, hyper_params"""
#     config: Config = attr.ib(factory=Config)
#     params: Params = attr.ib(factory=Params)
#     hyperparams: HyperParams = attr.ib(factory=HyperParams)

#     def __attrs_post_init__(self):
#         attr_dict = attr.asdict(self)
#         logging.debug(f"ExperimentConfig:\n{pformat(attr_dict)}\n")
