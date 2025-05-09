import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({'font.size': 17})


def convert_latency(val):
    if isinstance(val, str):
        if val.endswith("us"):
            return float(val.replace("us", "")) / 1000  # µs to ms
        elif val.endswith("ms"):
            return float(val.replace("ms", ""))  # already ms
    return pd.NA


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

def compare_resource_usage_plot(first_process, second_process):
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
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'hspace': 0.5})

    box_plot_path = f"metrics/plots/webserver/box_plot/nanos_and_docker_{field_pair[0]}.png"
    ax1.set_title(
        f"Distribution of {field_pair[1]} for Nanos")
    ax2.set_title(
        f"Distribution of {field_pair[1]} for Docker")
    plot_box_plot(ax1, nanos_df, field_pair)
    plot_box_plot(ax2, docker_df, field_pair)
    fig.savefig(box_plot_path)


    comparison_path = f"metrics/plots/comparitive/webserver/bar_plot/docker_vs_nanos_{field_pair[0]}.png"
    plot_bar_with_error(nanos_data, docker_data, field_pair, comparison_path)


def plot_box_plot(ax, data, field_pair):
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


# def plot_min_mean_max_graph(data, ylabel, path):
#     x = [10, 50, 100]
#     y = [float(data[str(val)]['mean']) for val in x]
#
#     fig, ax = plt.subplots()
#     ax.set_xticks(x)
#     ax.set_xlabel("Concurrent Connections")
#     ax.set_ylabel(ylabel)
#     ax.set_title(f"Min, Mean, Max Graph of {ylabel}.")
#     error_below = [float(data[str(val)]['mean']) -
#                    float(data[str(val)]['min']) for val in x]
#     error_above = [float(data[str(val)]['max']) -
#                    float(data[str(val)]['mean']) for val in x]
#     error = [error_below, error_above]
#
#     ax.errorbar(
#         x,
#         y,
#         yerr=error,
#         capsize=5,
#         ecolor="lightblue",
#         markerfacecolor="black",
#         markeredgecolor="black",
#         marker="o",
#         linestyle="none",
#     )
#
#     plt.savefig(path)
#     plt.close()

# Plotting function


def plot_bar_with_error(nanos_data, docker_data, field_pair, path):
    plt.rcParams.update({'font.size': 15.5})
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
        ax.bar_label(rects)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(field_pair[1])
    ax.set_title(f'Mean Latency for {field_pair[1]}')
    ax.set_xticks(x + width, platforms)
    if field_pair[0] == 'latency_avg':
        ax.legend(loc='upper left', bbox_to_anchor=(-0.02, 1.01))
    else:
        ax.legend(loc='lower right')

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
    compare_resource_usage_plot((
        "metrics/docker_usage_log.csv", "docker"), ("metrics/nanos_usage_log.csv", "nanos"))
    compare_webserver_metrics_plot(("metrics/webserver/webserver_metrics_nanos.csv", "nanos"), (
        "metrics/webserver/webserver_metrics_docker.csv", "docker"))
