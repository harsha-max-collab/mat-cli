"""Plotting utilities with multiple styles."""

import matplotlib.pyplot as plt
import numpy as np

# List of styles users can choose
AVAILABLE_STYLES = [
    "dark",
    "light",
    "seaborn",
    "ggplot",
    "bmh",
    "classic",
    "grayscale",
    "dark_background",
    "fivethirtyeight",
    "Solarize_Light2",
]

def list_styles():
    """Return all available style names."""
    return AVAILABLE_STYLES + plt.style.available


def apply_style(style: str = "dark"):
    """Apply a plotting style."""
    style = style.lower().strip()

    theme_map = {
        "dark": "dark_background",
        "light": "default",
        "seaborn": "seaborn-v0_8",
        "ggplot": "ggplot",
        "bmh": "bmh",
        "classic": "classic",
        "grayscale": "grayscale",
        "fivethirtyeight": "fivethirtyeight",
        "solarize": "Solarize_Light2",
    }

    if style in theme_map:
        plt.style.use(theme_map[style])
    elif style in plt.style.available:
        plt.style.use(style)
    else:
        plt.style.use("dark_background")
        print(f"Style '{style}' not found. Using dark_background instead.")


def plot_variable(
    data,
    title: str = "",
    plot_type: str = "auto",
    style: str = "dark",
    save: str = None,
    show: bool = True,
):
    """Plot a variable from a .mat file."""
    apply_style(style)
    arr = np.asarray(data)

    # Auto-detect plot type
    if plot_type == "auto":
        if arr.ndim == 1 or (arr.ndim == 2 and min(arr.shape) == 1):
            plot_type = "line"
        elif arr.ndim == 2:
            plot_type = "image"
        else:
            plot_type = "hist"

    fig, ax = plt.subplots(figsize=(10, 6))

    if plot_type == "line":
        ax.plot(arr.ravel())
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")

    elif plot_type == "image":
        im = ax.imshow(arr, aspect="auto", cmap="viridis")
        fig.colorbar(im, ax=ax)

    elif plot_type == "hist":
        ax.hist(arr.ravel(), bins=50)
        ax.set_xlabel("Value")
        ax.set_ylabel("Count")

    else:
        ax.plot(arr.ravel())

    ax.set_title(title or f"{plot_type} plot")
    fig.tight_layout()

    if save:
        fig.savefig(save, dpi=150, bbox_inches="tight")
        print(f"Saved plot to: {save}")

    if show:
        plt.show()
    else:
        plt.close()