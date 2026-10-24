import socket, time

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("0.0.0.0", 5000))
clients = {}                       # (ip, port) -> last_seen

while True:
    data, addr = server.recvfrom(2048)
    now = time.time()
    clients[addr] = now
    for peer in list(clients):
        if now - clients[peer] > 10:      # drop inactive clients
            del clients[peer]
        elif peer != addr:
            server.sendto(data, peer)     # relay to everyone else
