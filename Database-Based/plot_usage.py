import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
plt.rcParams.update({'font.size': 18})

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


def plot_database_metric(nanos_df, docker_df, field_pair):
    def prepare_data(df):
        result = {'10': {}, '50': {}, '100': {}}
        for connection in [10, 50, 100]:
            get_data = df[(df['connection'] == connection)
                          & (df['test'] == 'GET')]
            set_data = df[(df['connection'] == connection)
                          & (df['test'] == 'SET')]
            result[str(connection)]['min'] = {
                'GET': get_data[field_pair[0]].min(), 'SET': set_data[field_pair[0]].min()}
            result[str(connection)]['max'] = {
                'GET': get_data[field_pair[0]].max(), 'SET': set_data[field_pair[0]].max()}
            result[str(connection)]['mean'] = {
                'GET': get_data[field_pair[0]].mean(), 'SET': set_data[field_pair[0]].mean()}
        return result

    # Prepare data for nanos and docker
    nanos_data = prepare_data(nanos_df)
    docker_data = prepare_data(docker_df)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'hspace': 0.5})

    box_plot_path = f"metrics/plots/database/box_plot/nanos_and_docker_{field_pair[0]}.png"
    ax1.set_title(
        f"Distribution of {field_pair[1]} for Nanos")
    ax2.set_title(
        f"Distribution of {field_pair[1]} for Docker")
    plot_box_plot(ax1, nanos_df, field_pair)
    plot_box_plot(ax2, docker_df, field_pair)
    fig.savefig(box_plot_path)

    comparison_path = f"metrics/plots/comparitive/database/bar_plot/docker_vs_nanos_{field_pair[0]}.png"
    plot_bar_with_error(nanos_data, docker_data, field_pair, comparison_path)


def plot_box_plot(ax, data, field_pair):

    # Prepare data: group values by connection count
    connection_levels = [('GET', 10), ('SET', 10), ('GET', 50),
                         ('SET', 50), ('GET', 100), ('SET', 100)]
    data = [data[(data["connection"] == level[1]) & (data['test'] == level[0])]
            [field_pair[0]].dropna().tolist() for level in connection_levels]
    operation_colors = {
        'GET': 'orange',
        'SET': 'tomato'
    }
    labels = [f"({op}-{conn})" for op, conn in connection_levels]
    blt = ax.boxplot(data, tick_labels=labels, patch_artist=True)
    for patch, (op, _) in zip(blt['boxes'], connection_levels):
        patch.set_facecolor(operation_colors[op])
    ax.set_xlabel("(Operation, Parallel Connections)")
    ax.set_ylabel(field_pair[1])
    legend_patches = [mpatches.Patch(color=color, label=label)
                      for label, color in operation_colors.items()]
    ax.legend(handles=legend_patches, title="Operation")


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
    connection_levels = [('GET', 10), ('SET', 10), ('GET', 50),
                         ('SET', 50), ('GET', 100), ('SET', 100)]

    nanos_means = [nanos_data[str(conn)]['mean'][op]
                   for op, conn in connection_levels]
    docker_means = [docker_data[str(conn)]['mean'][op]
                    for op, conn in connection_levels]

    labels = [f"({op}-{conn})" for op, conn in connection_levels]
    x = np.arange(len(labels))

    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 7))

    rects1 = ax.bar(x - width/2 - 0.05, nanos_means,
                    width, label='Nanos', color='orange')
    rects2 = ax.bar(x + width/2 + 0.05, docker_means,
                    width, label='Docker', color='blue')

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    ax.set_ylabel(field_pair[1])
    ax.set_title(f'Mean {field_pair[1]} by Operation and Connection Count')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("(Operation, Parallel Connections)")
    ax.legend(loc='best')

    plt.savefig(path)
    plt.close()


def compare_database_metrics_plot(nanos_process, docker_process):
    nanos_df = pd.read_csv(nanos_process[0])
    docker_df = pd.read_csv(docker_process[0])
    nanos_df.rename(columns={'rps': 'requests_per_sec',
                    'avg_latency_ms': 'latency_avg'}, inplace=True)
    docker_df.rename(columns={'rps': 'requests_per_sec',
                     'avg_latency_ms': 'latency_avg'}, inplace=True)

    plot_database_metric(
        nanos_df, docker_df,
        field_pair=('requests_per_sec', 'Request per Second')
    )

    plot_database_metric(
        nanos_df, docker_df,
        field_pair=('latency_avg', 'Latency (in millisecond)')
    )


if __name__ == "__main__":
    compare_resource_usage_plot((
        "metrics/docker_usage_log.csv", "docker"), ("metrics/nanos_usage_log.csv", "nanos"))
    compare_database_metrics_plot(("metrics/database/database_metrics_nanos.csv", "nanos"), (
        "metrics/database/database_metrics_docker.csv", "docker"))
