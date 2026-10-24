import socket, struct, threading, time, pyaudio

SERVER = ("192.168.1.10", 5000)             # change to your server's IP
RATE, CHUNK, USER_ID = 16000, 320, 1         # 320 samples = 20 ms

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pa = pyaudio.PyAudio()
mic = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
              input=True, frames_per_buffer=CHUNK)
spk = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
              output=True, frames_per_buffer=CHUNK)

def send_loop():
    seq = 0
    while True:
        pcm = mic.read(CHUNK, exception_on_overflow=False)
        sock.sendto(struct.pack("!IH", seq, USER_ID) + pcm, SERVER)
        seq += 1

buffer, next_seq = {}, None
def recv_loop():
    while True:
        data, _ = sock.recvfrom(2048)
        seq, uid = struct.unpack("!IH", data[:6])
        buffer[seq] = data[6:]

def play_loop():
    global next_seq
    silence = b"\x00" * (CHUNK * 2)
    while True:
        if next_seq is None and len(buffer) >= 3:   # ~60 ms prefill
            next_seq = min(buffer)
        if next_seq is None:
            time.sleep(0.005); continue
        spk.write(buffer.pop(next_seq, silence))     # conceal if lost
        next_seq += 1

for fn in (send_loop, recv_loop, play_loop):
    threading.Thread(target=fn, daemon=True).start()
input("Voice chat running. Press Enter to quit.\n")
