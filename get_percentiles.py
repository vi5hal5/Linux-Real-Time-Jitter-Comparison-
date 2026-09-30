import os

def calculate_percentiles(file_path):
    if not os.path.exists(file_path):
        return f"File {file_path} not found."

    latencies = []
    hits = []
    
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            # Grab only the histogram rows
            if len(parts) > 1 and parts[0].isdigit():
                latency_val = int(parts[0])
                total_hits = sum(int(x) for x in parts[1:])
                
                if total_hits > 0:
                    latencies.append(latency_val)
                    hits.append(total_hits)

    total_data_points = sum(hits)
    if total_data_points == 0:
        return "No data found."

    # Calculate the threshold index for 99% and 99.9%
    p99_threshold = total_data_points * 0.99
    p999_threshold = total_data_points * 0.999
    
    p99 = 0
    p999 = 0
    running_sum = 0
    
    for lat, hit_count in zip(latencies, hits):
        running_sum += hit_count
        
        # Lock in the value once the running sum crosses the threshold
        if running_sum >= p99_threshold and p99 == 0:
            p99 = lat
        if running_sum >= p999_threshold and p999 == 0:
            p999 = lat
            
    return p99, p999

# Run calculations
print("--- VM Results ---")
vm_p99, vm_p999 = calculate_percentiles('vm_results.txt')
print(f"99th Percentile: {vm_p99} µs")
print(f"99.9th Percentile: {vm_p999} µs\n")

print("--- Bare-Metal Results ---")
bm_p99, bm_p999 = calculate_percentiles('baremetal_results.txt')
print(f"99th Percentile: {bm_p99} µs")
print(f"99.9th Percentile: {bm_p999} µs")