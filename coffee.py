"""Simulate one morning (7:00-11:00) at a coffee shop with a single barista."""

import numpy as np

OPEN_MINUTES = 4 * 60      # 7:00 to 11:00
MEAN_INTERARRIVAL = 3.0    # minutes between customers, on average
MIN_SERVICE, MAX_SERVICE = 1.0, 4.0


def simulate(rng):
    # Draw more gaps than needed, then keep the arrivals that fall before closing.
    expected = int(OPEN_MINUTES / MEAN_INTERARRIVAL)
    gaps = rng.exponential(MEAN_INTERARRIVAL, size=expected * 3)
    arrivals = np.cumsum(gaps)
    arrivals = arrivals[arrivals < OPEN_MINUTES]

    services = rng.uniform(MIN_SERVICE, MAX_SERVICE, size=arrivals.size)

    # The barista starts an order when the customer arrives or when the
    # previous order is done, whichever is later.
    waits = np.empty(arrivals.size)
    barista_free_at = 0.0
    for i, (arrival, service) in enumerate(zip(arrivals, services)):
        start = max(arrival, barista_free_at)
        waits[i] = start - arrival
        barista_free_at = start + service

    return waits


def main():
    rng = np.random.default_rng()
    waits = simulate(rng)
    print(f"Customers served: {waits.size}")
    if waits.size:
        print(f"Average wait: {waits.mean():.2f} minutes")


if __name__ == "__main__":
    main()
