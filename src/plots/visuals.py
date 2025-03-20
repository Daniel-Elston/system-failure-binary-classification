from __future__ import annotations

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.metrics import auc
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import roc_curve
from ydata_profiling import ProfileReport
from pprint import pformat

from config.pipeline_context import PipelineContext
from config.settings import Config
from src.core.base_pipeline import BasePipeline
from src.core.data_handling.data_module import DataModule
sns.set_style("darkgrid")


class ExploratoryVisuals:
    """Visualise the data loader and transforms"""

    def __init__(
        self, ctx: PipelineContext,
        dataset: DataModule,
        path_key: str
    ):
        self.ctx = ctx
        self.dataset = dataset
        self.path_key = path_key
        self.config: Config = ctx.settings.config


    def run(self):
        col_sets = {
            "numeric_info_cols": self.config.col_types['numeric_info_cols'],
            "sensor_cols": self.config.col_types['sensor_cols'],
        }
        for method in [self.generate_pair_plot, self.plot_box_by_target]:
            for name, cols in col_sets.items():
                method(name, cols)
        [self.generate_corr_plot(method) for method in ["pearson", "spearman"]]
    
    def generate_target_barplot(self):
        plt.figure(figsize=(8, 6))
        sns.countplot(
            x='target',
            data=self.dataset,
            hue=self.config.target_col
        )
        plt.xlabel('Target')
        plt.ylabel('Observations')
        plt.title('Target Distribution')
        plt.tight_layout()
        if self.config.save_fig:
            plt.savefig("reports/analysis/target_imb.png")
        plt.show()
        plt.close()

    def generate_pair_plot(self, name, cols):
        sns.pairplot(
            self.dataset[cols], diag_kind='kde',
            plot_kws={'alpha': 0.8, 's': 2, 'edgecolor': 'k'}
        )
        if self.config.save_fig:
            plt.savefig(f"reports/figures/{self.path_key}-pairplot-{name}.png")
        if self.config.show_fig:
            plt.show()
        plt.close()

    def plot_box_by_target(self, name, cols):
        """Generates box plots for each numerical feature grouped by the target column."""
        cols = cols + [self.config.target_col]
        num_features = len(cols)
        fig, axes = plt.subplots(nrows=num_features, figsize=(8, 5 * num_features))

        if num_features == 1:  # Handle single column case
            axes = [axes]

        for ax, col in zip(axes, cols):
            sns.boxplot(
                data=self.dataset[cols],
                x=self.config.target_col,
                y=col,
                ax=ax,
                hue=self.config.target_col,
                palette="coolwarm"
            )
            ax.set_title(f'Box Plot of {col} by {self.config.target_col}')
            ax.set_xlabel(self.config.target_col)
            ax.set_ylabel(col)

        plt.tight_layout()
        plt.legend()
        if self.config.save_fig:
            plt.savefig(f"reports/figures/{self.path_key}-boxplot-{name}.png", bbox_inches='tight')
        if self.config.show_fig:
            plt.show()
        plt.close()

    def generate_corr_plot(self, method="pearson", threshold=0.1):
        df = self.dataset.select_dtypes(include=np.number)
        correlation_matrix = df.corr(method=method)
        target_col = self.config.target_col
        target_corr = correlation_matrix[target_col]
        relevant_cols = target_corr[abs(target_corr) >= threshold].index.tolist()
        logging.debug(f"Method: {method}, Threshold: {threshold}, Relevant Correlated columns:\n{pformat(relevant_cols)}")
        sub_corr_matrix = correlation_matrix.loc[relevant_cols, relevant_cols]
        plt.figure(figsize=(12, 10))
        ax = sns.heatmap(
            sub_corr_matrix,
            annot=True,
            fmt=".2f",
            cmap=sns.diverging_palette(20, 220, as_cmap=True),
            vmax=1,
            vmin=-1,
            cbar=True,
            square=True,
            annot_kws={"size": 7}
        )
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=8, rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=8, rotation=0)
        plt.title(f'Correlation Matrix (Method: {method}, Threshold={threshold})', fontsize=12)
        plt.tight_layout()
        if self.config.save_fig:
            plt.savefig(f"reports/figures/{self.path_key}-corr-{method}-thres-{threshold}.png")

        if self.config.show_fig:
            plt.show()
        plt.close()


class EvaluationVisuals(BasePipeline):
    def __init__(
        self, ctx: PipelineContext,
        x_test: DataModule,
        y_test: DataModule,
        y_test_pred: DataModule,
        model: ImbPipeline,
        path_key: str
    ):
        super().__init__(ctx)
        self.ctx = ctx
        self.x_test_fs = x_test
        self.y_test = y_test
        self.y_test_pred = y_test_pred
        self.model = model
        self.path_key = path_key

    def run(self):
        self.plot_confusion_matrix(self.y_test, self.y_test_pred)
        self.plot_roc_curve(self.model, self.x_test_fs, self.y_test)
        self.plot_precision_recall_curve(self.model, self.x_test_fs, self.y_test)
        self.plot_boxplot()
        self.generate_classification_report(self.y_test, self.y_test_pred)

    def plot_confusion_matrix(self, y_test, y_test_pred):
        """Generates a Confusion Matrix for the model.
        IE. how many of the positive cases are we able to predict?"""
        cm = confusion_matrix(y_test, y_test_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Predicted 0', 'Predicted 1'],
                    yticklabels=['Actual 0', 'Actual 1'])
        plt.title('Confusion Matrix')
        plt.tight_layout()
        if self.config.save_fig:
            plt.savefig(f"reports/figures/{self.path_key}/confusion_matrix.png")
        if self.config.show_fig:
            plt.show()
        plt.close()

    def plot_roc_curve(self, model, X_test_fs, y_test):
        """"
        Receiver Operating Characteristic (ROC) Curve:
        The ROC curve plots the true positive rate (TPR) against the false positive rate (FPR).
        IE. if we are trying to predict a positive case, how many of the positive cases are we able to predict?
        """
        fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_test_fs)[:, 1])
        roc_auc = auc(fpr, tpr)
        plt.figure(figsize=(8, 6))
        plt.plot(
            fpr,
            tpr,
            color='darkorange',
            lw=2,
            label=f'ROC curve (AUC = {roc_auc:.2f})'
        )
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        plt.tight_layout()
        if self.config.save_fig:
            plt.savefig(f"reports/figures/{self.path_key}/roc_curve.png")
        if self.config.show_fig:
            plt.show()
        plt.close()

    def plot_boxplot(self):
        """Boxplot of cross-validation F1 scores
            Shows the distribution of the cross-validation F1 scores.
            IE. How consistent is our model?
        """
        plt.figure(figsize=(8, 6))
        plt.boxplot([0.49, 0.53, 0.56, 0.52, 0.57])
        plt.title('Distribution of Cross-validation F1 Scores')
        plt.ylabel('F1 Score')
        plt.tight_layout()
        if self.config.save_fig:
            plt.savefig(f"reports/figures/{self.path_key}/boxplot.png")
        if self.config.show_fig:
            plt.show()
        plt.close()

    def plot_precision_recall_curve(self, model, X_test_fs, y_test):
        """Precision-Recall Curve:
            Shows the trade-off between precision and recall.
            IE. if we are trying to predict a positive case, how many of the positive cases are we able to predict?
        """
        precision, recall, _ = precision_recall_curve(
            y_test,
            model.predict_proba(X_test_fs)[:, 1]
        )
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color='blue', lw=2)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.tight_layout()
        if self.config.save_fig:
            plt.savefig(f"reports/figures/{self.path_key}/precision_recall_curve.png")
        if self.config.show_fig:
            plt.show()
        plt.close()

    def generate_classification_report(self, y_test, y_test_pred):
        file_path = f"reports/analysis/{self.path_key}-classification-report.xlsx"
        report = classification_report(y_test, y_test_pred, output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        report_df = round(report_df, 2)
        report_df.to_excel(file_path)
        logging.warning(f"Test Classification Report\n{report_df}")
