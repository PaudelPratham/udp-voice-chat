import socket, struct, threading, time, math, random, sys, statistics
uid, secs, loss = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
log_pkts = len(sys.argv) > 4
RATE, CHUNK = 16000, 320
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.bind(("127.0.0.1", 0))
SERVER = ("127.0.0.1", 5000)
tag = f"[CLIENT-{uid}]"
print(f"{tag} Local socket {sock.getsockname()} -> server {SERVER}")
print(f"{tag} Audio: mono {RATE} Hz, 16-bit, frame = {CHUNK} samples (20 ms), test tone {440*uid} Hz")
print(f"{tag} Induced receive-side loss: {loss*100:.1f}%", flush=True)
buffer, stop = {}, False
sent = recvd = dropped = concealed = played = 0
lat, arr, first_t, prev_t = [], [], None, None
def tone(seq):
    return struct.pack("<320h", *[int(8000*math.sin(2*math.pi*440*uid*(seq*CHUNK+i)/RATE)) for i in range(CHUNK)])
def send_loop():
    global sent
    t0 = time.time()
    while not stop:
        pl = bytearray(tone(sent)); pl[0:8] = struct.pack("!d", time.time())   # test-only send timestamp
        sock.sendto(struct.pack("!IH", sent, uid) + bytes(pl), SERVER); sent += 1
        time.sleep(max(0, t0 + sent*0.02 - time.time()))
def recv_loop():
    global recvd, dropped, first_t, prev_t
    sock.settimeout(0.2)
    while not stop:
        try: data, _ = sock.recvfrom(2048)
        except socket.timeout: continue
        if random.random() < loss: dropped += 1; continue
        now = time.time(); seq, u = struct.unpack("!IH", data[:6]); recvd += 1
        if first_t is None: first_t = now
        if prev_t is not None: arr.append((now-prev_t)*1000)
        if log_pkts and recvd <= 10:
            print(f"{tag} RX  t=+{(now-first_t)*1000:7.1f} ms  seq={seq:<5} uid={u}  udp_payload={len(data)} B  (wire = {len(data)+28} B)  gap={(now-prev_t)*1000 if prev_t else 0:5.1f} ms", flush=True)
        prev_t = now; buffer[seq] = data[6:]
def play_loop():
    global played, concealed
    nxt = None; t0 = None
    while not stop:
        if nxt is None:
            if len(buffer) >= 3: nxt = min(buffer); t0 = time.time(); k = 0
            else: time.sleep(0.002); continue
        fr = buffer.pop(nxt, None); played += 1
        if fr is None: concealed += 1
        else: lat.append((time.time() - struct.unpack("!d", fr[:8])[0])*1000)
        nxt += 1; k += 1
        time.sleep(max(0, t0 + k*0.02 - time.time()))
for f in (send_loop, recv_loop, play_loop): threading.Thread(target=f, daemon=True).start()
time.sleep(secs); stop = True; time.sleep(0.3)
exp = max(1, recvd + dropped)
jit = statistics.pstdev(arr) if len(arr) > 1 else 0
print(f"{tag} ---- session summary ({secs:.0f} s) ----")
print(f"{tag} packets sent      : {sent}")
print(f"{tag} packets received  : {recvd}  (dropped by emulation: {dropped})")
print(f"{tag} frames played     : {played}  concealed (silence): {concealed}")
print(f"{tag} measured loss     : {dropped/exp*100:.1f} %")
print(f"{tag} playout latency   : avg {statistics.mean(lat):.1f} ms, max {max(lat):.1f} ms")
print(f"{tag} arrival jitter    : {jit:.2f} ms (std-dev of inter-arrival time)")
