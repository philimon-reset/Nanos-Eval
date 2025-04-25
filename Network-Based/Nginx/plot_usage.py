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

    plot_path = f"../metrics/plots/comparative_usage_plot.png"
    plt.savefig(plot_path)
    plt.close()
    print(f"📈 Plot saved to {plot_path}")

if __name__ == "__main__":
    original_process_log = ("metrics/docker_usage_log.csv", "docker")
    ops_process_log = ("metrics/ops_usage_log.csv", "ops")
    comparative_plot(original_process_log, ops_process_log)