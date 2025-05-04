# bar_width = 0.2
# connection_indices = [0, 1, 2, 3]  # 3 connections: 0, 1, 2
#
# fig, ax = plt.subplots(figsize=(12, 6))
# if field_pair[1] == 'Latency':
#     ax.set_ylim(0, max_val + 1)
#
# ax.bar([i - 1.5 * bar_width for i in connection_indices], nanos_data['10'] + docker_data['10'], width=bar_width,
#        label='10 Connections')
# ax.bar([i + 0.5 * bar_width for i in connection_indices], nanos_data['50'] + docker_data['50'], width=bar_width,
#        label='50 Connections')
# ax.bar([i - 0.5 * bar_width for i in connection_indices], nanos_data['100'] + docker_data['100'], width=bar_width,
#        label='100 Connections')
#
# ax.set_ylabel(field_pair[1])
# ax.set_title(f'Webserver Performance ({field_pair[1]})')
# group_centers = []
# for i in connection_indices:
#     bars_x_positions = [
#         i - 1.5 * bar_width,
#         i + 0.5 * bar_width,
#         i - 0.5 * bar_width,
#     ]
#     center = sum(bars_x_positions) / len(bars_x_positions)
#     group_centers.append(center)
#
# ax.set_xticks(group_centers)
# ax.set_xticklabels(['Nanos(10s)', 'Nanos(20s)', 'Docker(10s)', 'Docker(20s)'])
# ax.legend()
# ax.grid(axis='y')
#
# plt.tight_layout()
# plt.savefig(plot_path)
# plt.close()