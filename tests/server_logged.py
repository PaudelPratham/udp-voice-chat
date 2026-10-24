import socket, time, signal, sys
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("0.0.0.0", 5000))
server.settimeout(0.5)
print("[SERVER] UDP voice relay listening on 0.0.0.0:5000", flush=True)
clients, relayed, bytes_out, last, prev = {}, 0, 0, time.time(), -1
def done(*a):
    print(f"[SERVER] Shutting down. Total relayed: {relayed} packets ({bytes_out/1024:.1f} KiB)", flush=True); sys.exit(0)
signal.signal(signal.SIGTERM, done); signal.signal(signal.SIGINT, done)
while True:
    try: data, addr = server.recvfrom(2048)
    except socket.timeout: data = None
    now = time.time()
    if data:
        if addr not in clients:
            print(f"[SERVER] New client registered: {addr}  (active clients = {len(clients)+1})", flush=True)
        clients[addr] = now
        for peer in list(clients):
            if now - clients[peer] > 10: del clients[peer]
            elif peer != addr:
                server.sendto(data, peer); relayed += 1; bytes_out += len(data)
    if now - last >= 2:
        if relayed != prev: print(f"[SERVER] relayed={relayed} packets  clients={len(clients)}", flush=True)
        prev = relayed; last = now
