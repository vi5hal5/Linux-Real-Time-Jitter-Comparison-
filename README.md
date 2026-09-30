# OS Jitter Benchmarking: Virtualized Linux vs Bare-Metal

A direct benchmarking project comparing **Linux timer and scheduling jitter** between a virtualized environment and a native bare-metal system. By measuring microsecond-scale scheduling delays under heavy CPU and memory stress, this project evaluates the impact of virtualization on timing determinism and examines the limitations of a standard Linux kernel for time-critical applications.

## Objective

To experimentally characterize the **scheduling latency and timing jitter** of a standard Linux kernel under heavy computational load.

At a 1 kHz control frequency, a time-critical application expects a periodic execution interval of exactly **1,000 microseconds (1 ms)**. This benchmark evaluates whether a conventional Linux environment can maintain this timing requirement under system stress, and provides a baseline for comparison with **real-time operating systems (RTOS) and real-time Linux configurations**.

## Methodology & Test Environments

The benchmark evaluates the operating system's ability to wake a real-time thread at precisely defined intervals while the system is under heavy computational stress.

Each environment was tested across **3 independent runs** to determine whether observed worst-case latency was representative rather than a one-off anomaly.

### Workload Simulation — `stress-ng`

`stress-ng` was used to generate artificial system load across CPU, I/O, and virtual memory:

```bash
stress-ng --cpu 4 --io 2 --vm 1 --vm-bytes 1G --timeout 100s
```

### Latency Measurement — `cyclictest`

`cyclictest` was used to periodically wake a real-time thread every **1,000 µs** for 100,000 cycles using `SCHED_FIFO` real-time scheduling.

```bash
sudo cyclictest -l100000 -m -Sp90 -i1000 -h400 -q
```

The measured latency represents the delay between the expected timer wake-up and the actual execution of the real-time thread.

This latency can be influenced by **kernel scheduling, hardware interrupts, CPU contention, memory pressure, I/O activity, and virtualization overhead**.

## Test Environments

### 1. Bare-Metal Linux

* **CPU:** AMD Ryzen 7 6800H
* **Cores:** 8 cores / 16 threads
* **Available RAM:** ~14 GiB
* **Kernel:** Linux 6.17.0-35-generic
* **Kernel configuration:** `PREEMPT_DYNAMIC`
* **OS:** Ubuntu 24.04.1
* **Power mode:** Frequency boost enabled

### 2. Virtualized Linux

* **Hypervisor:** VirtualBox
* **Guest OS:** Ubuntu 64-bit
* **Virtual CPUs:** 4
* **Allocated RAM:** 5196 MB
* **Paravirtualization:** KVM

## Results

![Latency Comparison Histogram](latency_comparison.png)

*Logarithmic histogram comparing timer latency between the virtualized and bare-metal environments.*

| Metric                    |    Virtual Machine |   Bare-Metal Linux |
| ------------------------- | -----------------: | -----------------: |
| **Average Latency**       |            ~720 µs |             2–4 µs |
| **99th Percentile**       |             396 µs |             393 µs |
| **99.9th Percentile**     |             399 µs |             395 µs |
| **Maximum Latency**       | 59,864 µs (~60 ms) | 6,170 µs (~6.1 ms) |
| **1 kHz Deadline Impact** |  ~60 missed cycles |   ~6 missed cycles |

*The 99th and 99.9th percentile values should be extracted from the `cyclictest` results across all three runs.*

## Timing Determinism

The measurements demonstrate a significant difference in worst-case timing behavior between the virtualized and bare-metal environments.

Under heavy system load, the virtualized environment experienced a maximum latency of approximately **60 ms**, while the bare-metal system experienced approximately **6.1 ms**.

For a 1 kHz periodic task with a 1 ms deadline, these delays correspond to approximately:

* **Virtual machine:** up to ~60 consecutive missed execution periods
* **Bare metal:** up to ~6 consecutive missed execution periods

The results illustrate that **average latency alone is insufficient when evaluating time-critical systems**. The worst-case latency and tail of the latency distribution are critical when deterministic timing is required.

## Linux vs Real-Time Operating Systems

The bare-metal results show that removing virtualization overhead substantially improves timing behavior. However, the measured worst-case latency of approximately 6.1 ms still exceeds a strict 1 ms timing requirement.

This highlights an important distinction between **general-purpose Linux** and **real-time operating systems**.

A standard Linux kernel is optimized primarily for general-purpose throughput and responsiveness. It does not provide hard guarantees that a periodic task will execute within a specified deadline.

Real-time systems instead prioritize **bounded and predictable response times**, using mechanisms such as:

* Real-time scheduling policies
* Priority-based task scheduling
* Interrupt prioritization
* Reduced interrupt latency
* CPU isolation
* Preemption control
* Deterministic resource allocation

## Interrupt and Scheduling Latency

The observed jitter is not solely an operating-system scheduling phenomenon.

A real-time task can be delayed by:

**Hardware interrupts → interrupt handlers → kernel activity → scheduler → task execution**

Additional sources of latency include CPU frequency changes, cache effects, memory pressure, I/O activity, competing processes, and—in the virtualized envir
