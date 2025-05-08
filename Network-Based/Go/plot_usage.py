import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def convert_latency(val):
    if isinstance(val, str):
        if val.endswith("us"):
            return float(val.replace("us", "")) / 1000  # µs to ms
        elif val.endswith("ms"):
            return float(val.replace("ms", ""))  # already ms
    return pd.NA


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

    plt.savefig(plot_path)
    plt.close()
    print(f"📈 Plot saved to {plot_path}")


def compare_resource_usage_plot(first_process, second_process):
    first_df = pd.read_csv(first_process[0])
    second_df = pd.read_csv(second_process[0])

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


def plot_webserver_metric(nanos_df, docker_df, field_pair):
    def prepare_data(df):
        result = {'10': {}, '50': {}, '100': {}}
        for connection in [10, 50, 100]:
            temp = df[df['connection'] == connection]
            result[str(connection)]['min'] = temp[field_pair[0]].min()
            result[str(connection)]['max'] = temp[field_pair[0]].max()
            result[str(connection)]['mean'] = temp[field_pair[0]].mean()
        return result

    # Prepare data for nanos and docker
    nanos_data = prepare_data(nanos_df)
    docker_data = prepare_data(docker_df)

    nanos_min_max_path = f"metrics/plots/webserver/min_max/nanos_{field_pair[0]}.png"
    nanos_box_plot_path = f"metrics/plots/webserver/box_plot/nanos_{field_pair[0]}.png"

    plot_min_mean_max_graph(nanos_data, field_pair[1],  nanos_min_max_path)
    plot_box_plot(nanos_df, field_pair, nanos_box_plot_path)

    docker_min_max_path = f"metrics/plots/webserver/min_max/docker_{field_pair[0]}.png"
    docker_box_plot_path = f"metrics/plots/webserver/box_plot/docker_{field_pair[0]}.png"

    plot_min_mean_max_graph(docker_data, field_pair[1], docker_min_max_path)
    plot_box_plot(docker_df, field_pair, docker_box_plot_path)

    comparison_path = f"metrics/plots/comparitive/webserver/bar_plot/docker_vs_nanos_{field_pair[0]}.png"
    plot_bar_with_error(nanos_data, docker_data, field_pair, comparison_path)


def plot_box_plot(data, field_pair, path):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Prepare data: group values by connection count
    connection_levels = [10, 50, 100]
    data = [data[data["connection"] == level][field_pair[0]].dropna().tolist()
            for level in connection_levels]
    colors = ['peachpuff', 'orange', 'tomato']
    # Create the box plot
    blt = ax.boxplot(data, tick_labels=connection_levels, patch_artist=True)
    for patch, color in zip(blt['boxes'], colors):
        patch.set_facecolor(color)
    ax.set_xlabel("Concurrent Connections")
    ax.set_ylabel(field_pair[1])
    ax.set_title(f"Distribution of {field_pair[1]} by Connection Count")

    plt.savefig(path)
    plt.close()


def plot_min_mean_max_graph(data, ylabel, path):
    x = [10, 50, 100]
    y = [float(data[str(val)]['mean']) for val in x]

    fig, ax = plt.subplots()
    ax.set_xticks(x)
    ax.set_xlabel("Concurrent Connections")
    ax.set_ylabel(ylabel)
    ax.set_title(f"Min, Mean, Max Graph of {ylabel}.")
    error_below = [float(data[str(val)]['mean']) -
                   float(data[str(val)]['min']) for val in x]
    error_above = [float(data[str(val)]['max']) -
                   float(data[str(val)]['mean']) for val in x]
    error = [error_below, error_above]

    ax.errorbar(
        x,
        y,
        yerr=error,
        capsize=5,
        ecolor="lightblue",
        markerfacecolor="black",
        markeredgecolor="black",
        marker="o",
        linestyle="none",
    )

    plt.savefig(path)
    plt.close()

# Plotting function


def plot_bar_with_error(nanos_data, docker_data, field_pair, path):
    platforms = ["Nanos", "Docker"]
    connections = [10, 50, 100]
    means = {str(k): [nanos_data[str(k)]['mean'],
                      docker_data[str(k)]['mean']] for k in connections}
    x = np.arange(len(platforms))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(figsize=(10, 6))

    for attribute, measurement in means.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width,
                       label=f"{attribute} Connections")
        ax.bar_label(rects, padding=4)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(field_pair[1])
    ax.set_title(f'Mean Latency for {field_pair[1]}')
    ax.set_xticks(x + width, platforms)
    ax.legend(loc='best')

    plt.savefig(path)
    plt.close()


def compare_webserver_metrics_plot(nanos_process, docker_process):
    nanos_df = pd.read_csv(nanos_process[0])
    nanos_df["requests_per_sec"] = nanos_df["requests_per_sec"].astype(float)
    nanos_df["latency_avg"] = nanos_df["latency_avg"].apply(convert_latency)

    docker_df = pd.read_csv(docker_process[0])
    docker_df["requests_per_sec"] = docker_df["requests_per_sec"].astype(float)
    docker_df["latency_avg"] = docker_df["latency_avg"].apply(convert_latency)

    plot_webserver_metric(
        nanos_df, docker_df,
        field_pair=('requests_per_sec', 'Request per Second')
    )

    plot_webserver_metric(
        nanos_df, docker_df,
        field_pair=('latency_avg', 'Latency (in millisecond)')
    )


if __name__ == "__main__":
    # compare_resource_usage_plot((
    #     "metrics/docker_usage_log.csv", "docker"), ("metrics/nanos_usage_log.csv", "nanos"))
    compare_webserver_metrics_plot(("metrics/webserver/webserver_metrics_nanos.csv", "nanos"), (
        "metrics/webserver/webserver_metrics_docker.csv", "docker"))
