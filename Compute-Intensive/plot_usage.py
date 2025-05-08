import sys
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update({'font.size': 18})


def plot_metric(df1, df2, x_col, y_col, labels, title, ylabel, plot_path):
    """Reusable function to plot a metric."""
    plt.figure(figsize=(12, 6))
    plt.plot(df1[x_col], df1[y_col], label=labels[0], marker='o')
    plt.plot(df2[x_col], df2[y_col], label=labels[1], marker='x')
    plt.ylim(0, None)  # Set y-axis limit to start from 0
    plt.title(title)
    plt.xlabel("Time Elapsed (s)")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"📈 Plot saved to {plot_path}")


def comparative_plot(first_process, second_process):
    first_df = pd.read_csv(first_process[0])
    second_df = pd.read_csv(second_process[0])

    # Plot CPU usage
    cpu_plot_path = f"metrics/plots/comparitive/{first_process[1]}_vs_{second_process[1]}_cpu_usage.png"
    plot_metric(
        first_df, second_df,
        x_col="Time Elapsed", y_col="CPU%",
        labels=[
            f"{first_process[1]} CPU Usage (%)", f"{second_process[1]} CPU Usage (%)"],
        title="Comparative CPU Usage Over Time",
        ylabel="CPU Usage (%)",
        plot_path=cpu_plot_path
    )

    # Plot Memory usage
    memory_plot_path = f"metrics/plots/comparitive/{first_process[1]}_vs_{second_process[1]}_memory_usage.png"
    plot_metric(
        first_df, second_df,
        x_col="Time Elapsed", y_col="Memory(MB)",
        labels=[
            f"{first_process[1]} Memory Usage (MB)", f"{second_process[1]} Memory Usage (MB)"],
        title="Comparative Memory Usage Over Time",
        ylabel="Memory Usage (MB)",
        plot_path=memory_plot_path
    )


if __name__ == "__main__":
    original_process_log = (
        "metrics/docker_usage_log.csv", "docker")
    nanos_process_log = ("metrics/nanos_usage_log.csv", "nanos")
    comparative_plot(original_process_log, nanos_process_log)
