# Voice Chat Application using UDP

A small multi-user voice chat prototype that sends 20 ms audio frames over UDP through a relay server.
Course project for Computer Networks, Vellore Institute of Technology.

## How it works
- Each client captures 16 kHz, 16-bit mono audio in 20 ms frames (640 bytes).
- A 6-byte header (4-byte sequence number + 2-byte user ID) is added and the frame is sent as one UDP datagram.
- The relay server forwards each datagram to all other registered clients.
- The receiver keeps a ~60 ms jitter buffer ordered by sequence number and plays silence for missing frames (no retransmission).

## Files
| File | Purpose |
|---|---|
| `server.py` | UDP relay server (port 5000) |
| `client.py` | Voice client (capture, send, receive, playback) |
| `tests/` | Loopback test scripts (no microphone required) |

## Run
    pip install -r requirements.txt
    python server.py                 # on the server machine
    # edit SERVER in client.py, set a unique USER_ID, then on each client:
    python client.py

## Status and limitations
Research prototype: uncompressed PCM (~270 kbps per speaker), no encryption, authentication, echo cancellation or NAT traversal.

## Team
- Pratham Paudel (24BCE2940)
- [Team member 2]
- [Team member 3]
