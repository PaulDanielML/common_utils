from typing import Any

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
