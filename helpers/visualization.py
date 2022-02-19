from typing import Any, Union, List

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

__all__ = ["visualize_pt_image_tensor", "PLOTLY_DEF_LAYOUT"]

TorchTensor = Any

PLOTLY_DEF_LAYOUT = go.Layout(
    width=1000,
    height=600,
    title=dict(x=0.5, y=0.95, font=dict(family="Arial", size=25, color="#000000")),
    font=dict(family="Courier New, Monospace", size=15, color="#000000"),
)


def visualize_pt_image_tensor(tens: TorchTensor) -> None:
    plt.imshow(tens.permute(1, 2, 0).cpu().numpy())


def plot_num_feature_correlation(df: pd.DataFrame, target_columns: Union[List, str]):
    if isinstance(target_columns, str):
        target_columns = [target_columns]
    num_columns = (
        df.drop(columns=target_columns, errors="ignore").select_dtypes("number").columns.tolist()
    )

    df_corr = (
        df[num_columns + target_columns]
        .corr()[target_columns]
        .drop(index=target_columns)
        .sort_values(by=target_columns)
    )

    return (
        go.Figure(
            data=go.Heatmap(
                z=df_corr.values,
                y=df_corr.index.tolist(),
                x=[c + " correlations" for c in target_columns],
            )
        )
        .update_layout(PLOTLY_DEF_LAYOUT)
        .update_layout(
            width=800 + 50 * len(target_columns),
            height=800,
            title_text=f"Correlation of Cont. columns - {', '.join(target_columns)}",
        )
        .update_yaxes(nticks=len(df_corr))
    )