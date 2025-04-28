import matplotlib.pyplot as plt
import pandas as pd

def comparative_plot(first_process, second_process):
    first_df = pd.read_csv(first_process[0])
    second_df = pd.read_csv(second_process[0])

    plt.figure(figsize=(12, 6))
    plt.plot(first_df["Time Elapsed"], first_df["CPU%"], label=f"{first_process[1]} CPU Usage (%)")
    plt.plot(second_df["Time Elapsed"], second_df["CPU%"], label=f"({second_process[1]}) CPU Usage (%)")
    plt.plot(first_df["Time Elapsed"], first_df["Memory(MB)"], label=f"({first_process[1]}) Memory Usage (MB)")
    plt.plot(second_df["Time Elapsed"], second_df["Memory(MB)"], label=f"({second_process[1]}) Memory Usage (MB)")

    plt.title("Comparative Resource Usage Over Time")
    plt.xlabel("Time Elapsed (s)")
    plt.ylabel("Usage")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plot_path = f"metrics/plots/comparative_usage_plot.png"
    plt.savefig(plot_path)
    plt.close()
    print(f"📈 Plot saved to {plot_path}")


def comparetive_webserver_plot():
    docker_df = pd.read_csv("metrics/webserver/webserver_metrics_docker_host.csv")
    ops_df = pd.read_csv("metrics/webserver/webserver_metrics_nanos.csv")
    plot_individual(docker_df, "Docker Host Metrics")
    plot_individual(ops_df, "Nanos Metrics")

def plot_individual(df, title):
    plt.figure(figsize=(10, 6))
    if df.select_dtypes(include=['number']).shape[1] == 1:
        # If only one numeric column, line plot
        df.plot(y=df.select_dtypes(include=['number']).columns[0], title=title)
    else:
        # If multiple numeric columns, line plot of all
        df.plot(y=df.select_dtypes(include=['number']).columns, title=title)
    plt.xlabel("Time Elapsed (s)")
    plt.ylabel("Usage")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plot_path = f"metrics/plots/webservers/{title}_webserver_metric_plot.png"
    plt.savefig(plot_path)
    plt.close()

if __name__ == "__main__":
    original_process_log = ("metrics/docker_host_usage_log.csv", "docker")
    ops_process_log = ("metrics/ops_usage_log.csv", "ops")
    comparative_plot(original_process_log, ops_process_log)
    comparetive_webserver_plot()