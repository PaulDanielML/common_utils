from typing import Dict, List, Union
from sklearn.metrics import confusion_matrix
import pandas as pd

from matplotlib import pyplot as plt
import seaborn as sn
import torch
import torchmetrics


def calculate_f1_score(
    preds: Union[List, torch.Tensor], target: Union[List, torch.Tensor], average: str = "micro"
):
    if type(preds) == list:
        preds = torch.as_tensor(preds)
    if type(target) == list:
        target = torch.as_tensor(target)

    number_of_classes = max(max(target).item(), max(preds).item()) + 1
    score = torchmetrics.functional.f1_score(
        preds=preds, target=target, average=average, num_classes=number_of_classes
    ).item()
    return score


def get_cm_from_predictions(
    y_true: List, y_pred: List, encoding: Dict, normalize: str = "true"
) -> pd.DataFrame:
    """
    Set normalize to None to get absolute numbers.
    """
    reverse_encoding = {v: k for k, v in encoding.items()}

    classes = [reverse_encoding[i] for i in set(y_pred).union(set(y_true))]

    cf_matrix = confusion_matrix(y_true, y_pred, normalize=normalize)

    df = pd.DataFrame(
        cf_matrix,
        index=classes,
        columns=classes,
    ).round(2)
    return df


def plot_and_save_dual_cm(df_A: pd.DataFrame, df_B: pd.DataFrame, save_to_file: str):
    """
    Visualizes two confusion matrices next to each other. Input format of df_A and df_B matches
    output of 'get_cm_from_predictions'.
    """

    fig, axes = plt.subplots(1, 2, figsize=(45, 20), constrained_layout=True)
    fig.suptitle("Confusion Matrices A & B", fontsize=30)

    sn.heatmap(df_A, annot=True, ax=axes[0])
    sn.heatmap(df_B, annot=True, ax=axes[1])
    axes[0].set_title("A", fontsize=25)
    axes[1].set_title("B", fontsize=25)
    axes[0].set_ylabel("True A", fontsize=20)
    axes[0].set_xlabel("Predicted A", fontsize=20)
    axes[1].set_ylabel("True B", fontsize=20)
    axes[1].set_xlabel("Predicted B", fontsize=20)
    axes[0].set_aspect("equal")
    axes[1].set_aspect("equal")

    plt.setp(axes[0].yaxis.get_majorticklabels(), rotation="horizontal")
    plt.setp(axes[1].yaxis.get_majorticklabels(), rotation="horizontal")
    plt.setp(axes[0].xaxis.get_majorticklabels(), rotation="vertical")
    plt.setp(axes[1].xaxis.get_majorticklabels(), rotation="vertical")

    fig.savefig(save_to_file, format="png")
    return fig
