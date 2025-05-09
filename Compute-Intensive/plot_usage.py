import sys
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update({'font.size': 18})


def plot_metric(ax, df1, df2, x_col, y_col, labels, fig_title, ylabel):
    """Reusable function to plot a metric."""
    ax.plot(df1[x_col], df1[y_col], label=labels[0], marker='o')
    ax.plot(df2[x_col], df2[y_col], label=labels[1], marker='x')
    ax.set_ylim(0, None)  # Set y-axis limit to start from 0
    ax.legend()
    ax.grid(True)
    ax.set_title(fig_title)
    ax.set_xlabel("Time Elapsed (s)")
    ax.set_ylabel(ylabel)

def comparative_plot(first_process, second_process):
    first_df = pd.read_csv(first_process[0])
    second_df = pd.read_csv(second_process[0])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Plot CPU usage
    plot_path = f"metrics/plots/comparitive/{first_process[1]}_vs_{second_process[1]}_resource_usage.png"
    plot_metric(
        ax1,
        first_df, second_df,
        x_col="Time Elapsed", y_col="CPU%",
        labels=[
            f"{first_process[1]} CPU Usage (%)", f"{second_process[1]} CPU Usage (%)"],
        fig_title="Comparative CPU Usage Over Time",
        ylabel="CPU Usage (%)"
    )

    # Plot Memory usage
    plot_metric(
        ax2,
        first_df, second_df,
        x_col="Time Elapsed", y_col="Memory(MB)",
        labels=[
            f"{first_process[1]} Memory Usage (MB)", f"{second_process[1]} Memory Usage (MB)"],
        fig_title="Comparative Memory Usage Over Time",
        ylabel="Memory Usage (MB)"
    )
    fig.tight_layout()
    fig.savefig(plot_path)
    print(f"📈 Plot saved to {plot_path}")



if __name__ == "__main__":
    original_process_log = (
        "metrics/docker_usage_log.csv", "docker")
    nanos_process_log = ("metrics/nanos_usage_log.csv", "nanos")
    comparative_plot(original_process_log, nanos_process_log)
