import matplotlib.pyplot as plt
import pandas as pd

def plot_metrics(first_process, second_process):
    first_df = pd.read_csv(first_process)
    second_df = pd.read_csv(second_process)

    plt.figure(figsize=(12, 6))
    plt.plot(first_df["Time Elapsed"], first_df["CPU%"], label=f"(Non Unikernel) CPU Usage (%)")
    plt.plot(first_df["Time Elapsed"], first_df["Memory(MB)"], label=f"(Non Unikernel) Memory Usage (MB)")

    plt.plot(second_df["Time Elapsed"], second_df["CPU%"], label=f"(Nanos) CPU Usage (%)")
    plt.plot(second_df["Time Elapsed"], second_df["Memory(MB)"], label=f"(Nanos) Memory Usage (MB)")

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

if __name__ == "__main__":
    original_process_log = "metrics/python3_usage_log.csv"
    ops_process_log = "metrics/ops_usage_log.csv"
    plot_metrics(original_process_log, ops_process_log)