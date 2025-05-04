test = ['"SET","43122.04","0.174","0.072","0.167","0.247","0.327","3.311",10,100000',
        '"GET","43802.02","0.166","0.064","0.167","0.231","0.311","2.015",10,100000']
FIELDNAMES = ['test', 'rps', 'avg_latency_ms', 'min_latency_ms', 'p50_latency_ms',
              'p95_latency_ms', 'p99_latency_ms', 'max_latency_ms', 'connection', 'requests']
for idx, row in enumerate(test):
    processed_row = []
    for x in row.split(","):
        x = x.strip('"')
        try:
            x = float(x)
        except ValueError:
            pass
        processed_row.append(x)
    test[idx] = dict(zip(FIELDNAMES, processed_row))
print(test)
