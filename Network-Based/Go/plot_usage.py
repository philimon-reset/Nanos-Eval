import sys
import matplotlib.pyplot as plt
import pandas as pd


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


def compare_resource_usage_plot(first_process, second_process):
    first_df = pd.read_csv(first_process[0])
    second_df = pd.read_csv(second_process[0])


    cpu_plot_path = f"metrics/plots/({sys.platform})/{first_process[1]}_vs_{second_process[1]}_cpu_usage.png"
    plot_metric(
        first_df, second_df,
        x_col="Time Elapsed", y_col="CPU%",
        labels=[
            f"{first_process[1]} CPU Usage (%)", f"{second_process[1]} CPU Usage (%)"],
        title="Comparative CPU Usage Over Time",
        ylabel="CPU Usage (%)",
        plot_path=cpu_plot_path
    )


    memory_plot_path = f"metrics/plots/({sys.platform})/{first_process[1]}_vs_{second_process[1]}_memory_usage.png"
    plot_metric(
        first_df, second_df,
        x_col="Time Elapsed", y_col="Memory(MB)",
        labels=[
            f"{first_process[1]} Memory Usage (MB)", f"{second_process[1]} Memory Usage (MB)"],
        title="Comparative Memory Usage Over Time",
        ylabel="Memory Usage (MB)",
        plot_path=memory_plot_path
    )




def plot_webserver_metric(docker_process_log, nanos_process_log, plot_path, field_pair):
    df1 = pd.read_csv(nanos_process_log[0])
    df2 = pd.read_csv(docker_process_log[0])
    max_val = float('-inf')
    def prepare_data(df):
        nonlocal max_val
        result = {'10': [], '50': [], '100': []}
        for connection in [10, 50, 100]:
            temp = df[df['connection'] == connection]
            for _, row in temp.iterrows():
                value = row[field_pair[0]]
                if field_pair[0] == 'latency_avg':
                    if 'us' in value:
                        value = float(value[:-2]) / 1000
                    else:
                        value = float(value[:-2])
                    max_val = max(max_val, value)
                result[str(connection)].append(value)
        return result

    # Prepare data for nanos and docker
    nanos_data = prepare_data(df1)
    docker_data = prepare_data(df2)

    bar_width = 0.2
    connection_indices = [0, 1, 2, 3]  # 3 connections: 0, 1, 2


    fig, ax = plt.subplots(figsize=(12, 6))
    if field_pair[1] == 'Latency':
        ax.set_ylim(0, max_val + 1)

    ax.bar([i - 1.5 * bar_width for i in connection_indices], nanos_data['10'] + docker_data['10'], width=bar_width, label='10 Connections')
    ax.bar([i + 0.5 * bar_width for i in connection_indices], nanos_data['50'] + docker_data['50'], width=bar_width, label='50 Connections')
    ax.bar([i - 0.5 * bar_width for i in connection_indices], nanos_data['100'] + docker_data['100'], width=bar_width, label='100 Connections')

    ax.set_ylabel(field_pair[1])
    ax.set_title(f'Webserver Performance ({field_pair[1]})')
    group_centers = []
    for i in connection_indices:
        bars_x_positions = [
            i - 1.5 * bar_width,
            i + 0.5 * bar_width,
            i - 0.5 * bar_width,
        ]
        center = sum(bars_x_positions) / len(bars_x_positions)
        group_centers.append(center)

    ax.set_xticks(group_centers)
    ax.set_xticklabels(['Nanos(10s)', 'Nanos(20s)', 'Docker(10s)', 'Docker(20s)'])
    ax.legend()
    ax.grid(axis='y')

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()


def compare_webserver_metrics_plot(first_process, second_process):

    request_metric_path = f"metrics/plots/({sys.platform})/{first_process[1]}_vs_{second_process[1]}_request_per_second.png"
    plot_webserver_metric(
        first_process, second_process,
        plot_path=request_metric_path,
        field_pair=('requests_per_sec', 'Request per Second')
    )

    request_metric_path = f"metrics/plots/({sys.platform})/{first_process[1]}_vs_{second_process[1]}_latency.png"
    plot_webserver_metric(
        first_process, second_process,
        plot_path=request_metric_path,
        field_pair=('latency_avg', 'Latency (in millisecond)')
    )


if __name__ == "__main__":
    # compare_resource_usage_plot((
    #     "metrics/docker_usage_log.csv", "docker"), ("metrics/ops_usage_log.csv", "nanos"))
    compare_webserver_metrics_plot((
        "metrics/webserver/webserver_metrics_docker.csv", "docker"), ("metrics/webserver/webserver_metrics_nanos.csv", "nanos"))
