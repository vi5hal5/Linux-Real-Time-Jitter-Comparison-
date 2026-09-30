# OS-Jitter-Benchmarking-for-Robotics

A direct benchmarking project comparing standard Linux timer jitter on a Virtual Machine versus a native bare-metal dual-boot setup. By measuring microsecond scheduling delays during high CPU and RAM stress, this repository highlights the practical impact of virtualization on timing stability and evaluates baseline OS suitability for time-critical robotic controllers.

## Objective
To experimentally characterize the scheduling latency (jitter) of a standard Linux kernel under heavy computational load. At a standard 1 kHz industrial control frequency, a robotic controller expects a position update exactly every 1,000 microseconds (1 ms). This comparison evaluates whether a standard virtualized or bare-metal OS environment can guarantee that deterministic operating envelope before deploying middleware like ROS 2 or DDS.

## Methodology & Test Environments
The benchmark evaluates the OS scheduler's ability to wake a sleeping thread exactly on time while the system is saturated with extreme artificial stress. Each environment was tested across 3 separate runs to ensure the worst-case jitter was a consistent distribution rather than a one-off anomaly.

*   **Workload Simulation (`stress-ng`):** 
    Used to simulate a heavy industrial compute load running in the background (stressing CPU, I/O, and Virtual Memory).
    `stress-ng --cpu 4 --io 2 --vm 1 --vm-bytes 1G --timeout 100s`
*   **Latency Measurement (`cyclictest`):** 
    Used to trigger a timer every 1,000 µs for 100,000 cycles using `SCHED_FIFO` real-time priority, measuring the exact microsecond delay of the OS response.
    `sudo cyclictest -l100000 -m -Sp90 -i1000 -h400 -q`

**Environments Tested:**
1.  **Bare-Metal (Host):** AMD Ryzen 7 6800H (8 Cores / 16 Threads), ~14 GiB available RAM. 
    *   *Power Mode:* Frequency boost enabled (CPU scaling 47%). 
    *   *Kernel:* Linux 6.17.0-35-generic SMP PREEMPT_DYNAMIC (Ubuntu 24.04.1).
2.  **Virtual Machine:** VirtualBox running Ubuntu (64-bit)[cite: 2]. 
    *   *Hardware Allocation:* 4 processor cores and 5196 MB base memory[cite: 2]. 
    *   *Acceleration:* KVM Paravirtualization enabled[cite: 2].

## Results & Data Comparison

latency_comparison.png

| Metric | Virtual Machine (Ubuntu) | Bare-Metal (AMD Ryzen 7) |
| :--- | :--- | :--- |
| **Average Latency** | ~720 µs | 2 - 4 µs |
| **99th Percentile** | [Insert Data] µs | [Insert Data] µs |
| **99.9th Percentile**| [Insert Data] µs | [Insert Data] µs |
| **Max Jitter (Worst-Case)** | 59,864 µs (~60 ms) | 6,170 µs (~6.1 ms) |
| **1 kHz Control Loop Impact** | Missed ~60 consecutive deadlines | Missed ~6 consecutive deadlines |

*Note: You will need to extract the 99th and 99.9th percentile values from your `cyclictest` output across the 3 runs to fill in the table above, proving the maximum latency was not a fluke.*

## Industrial Consequence
The data demonstrates the severe impact of virtualization overhead on timing determinism. Under simulated load, the virtual machine's OS scheduler was interrupted for nearly 60 milliseconds at its worst. In a 1 kHz distributed robotics system, this means the control software effectively goes blind for 60 consecutive cycles. On a physical machine, missing 60 control deadlines would risk trajectory deviation. 

Running the exact same load directly on bare-metal hardware yielded a 10x improvement in worst-case jitter (dropping from 60 ms to 6.1 ms). 

## Missing Baseline & Future Work
While the bare-metal hardware vastly outperforms the virtualized environment, this comparison indicates that standard Linux is still insufficient for high-speed robotics. The bare-metal maximum jitter of 6.1 ms still exceeds a strict 1 ms deadline. 

It should be plainly noted that this baseline benchmark tested a standard `PREEMPT_DYNAMIC` kernel. We did not yet test a `PREEMPT_RT` patched kernel or implement strict user-space CPU core isolation (e.g., `isolcpus`). Evaluating these real-time OS configurations to guarantee strict sub-millisecond determinism remains the immediate next step for future work.
