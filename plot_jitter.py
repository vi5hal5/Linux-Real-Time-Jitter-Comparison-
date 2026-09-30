import matplotlib.pyplot as plt
import os

def parse_cyclictest_data(file_path):
    latencies = []
    hits = []
    max_latency = 0
    
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found. Please ensure the file names are exact.")
        return latencies, hits, max_latency

    with open(file_path, 'r') as file:
        for line in file:
            # Extract Max Latency from the summary section
            if line.startswith("# Max Latencies:"):
                max_latencies = [int(x) for x in line.split()[3:]]
                max_latency = max(max_latencies)
                
            # Parse the histogram buckets
            parts = line.split()
            if len(parts) > 1 and parts[0].isdigit():
                latency_val = int(parts[0])
                total_hits = sum(int(x) for x in parts[1:])
                
                # FIX: Only plot points that actually have data to prevent Log-Scale crashes
                if total_hits > 0:
                    latencies.append(latency_val)
                    hits.append(total_hits)
                
    return latencies, hits, max_latency

# 1. Parse the data
vm_x, vm_y, vm_max = parse_cyclictest_data('vm_results.txt')
bm_x, bm_y, bm_max = parse_cyclictest_data('baremetal_results.txt')

# 2. Setup the graph
plt.figure(figsize=(12, 6))

# Plot the histograms (Logarithmic Y-axis because standard hits are in the thousands)
plt.plot(vm_x, vm_y, color='red', alpha=0.7, label='Virtual Machine (VM) Histogram')
plt.plot(bm_x, bm_y, color='blue', alpha=0.7, label='Bare-Metal Linux Histogram')

# 3. Add Vertical Lines for Worst-Case Max Jitter
if vm_max > 0:
    plt.axvline(x=vm_max, color='darkred', linestyle='--', linewidth=2, 
                label=f'VM Max Jitter: {vm_max} µs')
if bm_max > 0:
    plt.axvline(x=bm_max, color='darkblue', linestyle='--', linewidth=2, 
                label=f'Bare-Metal Max Jitter: {bm_max} µs')

# 4. Format the Graph
plt.yscale('log') # Log scale helps visualize both massive spikes and tiny outliers
plt.title('OS Scheduling Latency (Jitter) Benchmark: VM vs Bare-Metal', fontsize=14, fontweight='bold')
plt.xlabel('Latency / Jitter (Microseconds)', fontsize=12)
plt.ylabel('Frequency (Hit Count - Log Scale)', fontsize=12)
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(loc='upper right', fontsize=10)

# 5. Save and Show
plt.tight_layout()
plt.savefig('latency_comparison.png', dpi=300)
print("Graph successfully generated and saved as 'latency_comparison.png'")
plt.show()