"""
Quantara Instrumentation Visualizer
-----------------------------------
A lightweight simulation of coherence telemetry (κ, Δφ, Ω)
for AI alignment observability frameworks.

Displays dynamic coherence feedback in real time.
"""

import time
import math
import random
import matplotlib.pyplot as plt

def coherence_stream(duration=30, interval=0.2):
    """Simulate evolving κ/Δφ/Ω values over time."""
    t, kappa, delta_phi, omega = [], [], [], []
    base = random.uniform(0.7, 0.9)
    for i in range(int(duration / interval)):
        t.append(i * interval)
        k = base + random.uniform(-0.05, 0.05)
        dphi = abs(math.sin(i * 0.3)) * random.uniform(0.05, 0.15)
        om = 1 - abs(k - base)
        kappa.append(k)
        delta_phi.append(dphi)
        omega.append(om)
        time.sleep(interval)
    return t, kappa, delta_phi, omega

def visualize_coherence():
    """Real-time animated coherence telemetry plot."""
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title("Quantara Coherence Telemetry (κ / Δφ / Ω)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Normalized Value")
    line1, = ax.plot([], [], label='κ (alignment)', lw=2)
    line2, = ax.plot([], [], label='Δφ (deviation)', lw=2)
    line3, = ax.plot([], [], label='Ω (recovery)', lw=2)
    ax.legend()

    t_data, k_data, d_data, o_data = [], [], [], []
    start_time = time.time()

    for _ in range(150):
        elapsed = time.time() - start_time
        k = 0.8 + random.uniform(-0.05, 0.05)
        dphi = abs(math.sin(elapsed * 0.5)) * random.uniform(0.05, 0.15)
        omega = 1 - abs(k - 0.8)
        t_data.append(elapsed)
        k_data.append(k)
        d_data.append(dphi)
        o_data.append(omega)
        line1.set_data(t_data, k_data)
        line2.set_data(t_data, d_data)
        line3.set_data(t_data, o_data)
        ax.set_xlim(max(0, elapsed - 20), elapsed + 2)
        ax.set_ylim(0, 1.2)
        plt.pause(0.1)

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    visualize_coherence()
