from typing import Any

import matplotlib.pyplot as plt

TorchTensor = Any

def visualize_pt_image_tensor(tens: TorchTensor) -> None:
    plt.imshow(tens.permute(1, 2, 0).cpu().numpy())