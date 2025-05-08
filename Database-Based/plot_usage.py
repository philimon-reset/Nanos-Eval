import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    plt.rcParams.update({'font.size': 18})
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

    nanos_box_plot_path = f"metrics/plots/database/box_plot/nanos_{field_pair[0]}.png"
    plot_box_plot(nanos_df, field_pair, nanos_box_plot_path)

    docker_box_plot_path = f"metrics/plots/database/box_plot/docker_{field_pair[0]}.png"
    plot_box_plot(docker_df, field_pair, docker_box_plot_path)

    comparison_path = f"metrics/plots/comparitive/database/bar_plot/docker_vs_nanos_{field_pair[0]}.png"
    plot_bar_with_error(nanos_data, docker_data, field_pair, comparison_path)


def plot_box_plot(data, field_pair, path):
    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(figsize=(10, 6))

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
    ax.set_title(
        f"Distribution of {field_pair[1]} by Connection Count and Operation.")

    legend_patches = [mpatches.Patch(color=color, label=label)
                      for label, color in operation_colors.items()]
    ax.legend(handles=legend_patches, title="Operation")

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
