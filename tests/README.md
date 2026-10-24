# Loopback test scripts

No microphone needed; a test tone replaces the mic.

    python3 tests/server_logged.py            # terminal 1
    python3 tests/client_sim.py 1 10 0.0      # terminal 2: user 1, 10 s, 0% loss
    python3 tests/client_sim.py 2 10 0.0      # terminal 3
    python3 tests/client_sim.py 1 10 0.05     # same, with 5% induced receive-side loss
