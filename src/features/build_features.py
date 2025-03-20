from __future__ import annotations

import logging

from config.pipeline_context import PipelineContext
from config.settings import Config
from src.core.data_handling.data_module import DataModule


class BuildFeatures:
    def __init__(
        self, ctx: PipelineContext,
        dataset: DataModule,
    ):
        self.ctx = ctx
        self.dataset = dataset
        self.config: Config = ctx.settings.config

    def run(self):
        steps = [
            ('interaction_features', self.interaction_features),
            ('ratio_features', self.ratio_features),
            ('aggregate_sensor_features', self.aggregate_sensor_features),
            ('binary_threshold_features', self.binary_threshold_features),
            ('pairwise_sensor', self.pairwise_sensor),
            ('flow_by_loc', self.flow_by_loc),
            ('pop_target_to_end', self.pop_target_to_end)
        ]
        df = self.dataset
        for name, func in steps:
            logging.info(f"Building Feature: {name}")
            df = func(df)
        return {'feature-eng': df}

    def interaction_features(self, df):
        """Create polynomial and interaction features"""
        df['flow_max_interaction'] = df['flow_rate'] * df['max_output_rate']
        df['comp_age_squared'] = df['comp_age'] ** 2
        df['flow_rate_squared'] = df['flow_rate'] ** 2
        return df

    def ratio_features(self, df):
        """Generate ratio-based efficiency metrics"""
        df['efficiency_ratio'] = df['flow_rate'] / (df['max_output_rate'])
        df['maintenance_run_ratio'] = df['days_since_maintenance'] / (df['monthly_run_time'])

        df["maintenance_density"] = df["comp_age"] / (df["days_since_maintenance"] + 1)
        df["usage_per_maintenance"] = df["monthly_run_time"] / (df["days_since_maintenance"] + 1)
        df["time_weighted_efficiency"] = (df["comp_age"] * df["flow_rate"]) / (df["max_output_rate"] + 1)
        return df

    def aggregate_sensor_features(self, df):
        """Compute aggregated statistics for sensor readings"""
        sensor_cols = self.config.col_types['sensor_cols']
        df['sensor_avg'] = df[sensor_cols].mean(axis=1)
        df['sensor_range'] = df[sensor_cols].max(axis=1) - df[sensor_cols].min(axis=1)
        df['sensor_variability'] = df[sensor_cols].std(axis=1)
        df["sensor_skew"] = df[sensor_cols].skew(axis=1)
        df["sensor_kurt"] = df[sensor_cols].kurt(axis=1)

        df["sensor_max"] = df[sensor_cols].max(axis=1)
        df["sensor_min"] = df[sensor_cols].min(axis=1)

        # Sum of highly skewed sensors
        skewed_sensors = ['s1', 's2', 's3', 's6']
        df['sensor_skewed_sum'] = df[skewed_sensors].sum(axis=1)
        return df

    def binary_threshold_features(self, df):
        """Create binary indicators based on feature thresholds"""
        df['high_flow_rate'] = (df['flow_rate'] > 0.996).astype(int)
        df['high_output_rate'] = (df['max_output_rate'] > 150).astype(int)
        return df

    def pairwise_sensor(self, df):
        sensor_cols = self.config.col_types['sensor_cols']
        epsilon = 1e-9

        for i in range(len(sensor_cols)):
            for j in range(i + 1, len(sensor_cols)):
                col_i = sensor_cols[i]
                col_j = sensor_cols[j]

                # Ratio: sensor_i / sensor_j
                ratio_col_name = f"{col_i}_{col_j}_ratio"
                df[ratio_col_name] = df[col_i] / (df[col_j] + epsilon)

                inv_ratio_col_name = f"{col_j}_{col_i}_ratio"
                df[inv_ratio_col_name] = df[col_j] / (df[col_i] + epsilon)
        return df

    def flow_by_loc(self, df):
        loc_agg = df.groupby("loc")["flow_rate"].mean().rename("flow_rate_loc_mean")
        df = df.merge(loc_agg, on="loc", how="left")
        df["flow_rate_loc_ratio"] = df["flow_rate"] / (df["flow_rate_loc_mean"] + 1e-6)
        return df

    def pop_target_to_end(self, df):
        df["target"] = df.pop("target")
        return df
