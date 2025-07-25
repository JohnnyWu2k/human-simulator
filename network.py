import socket
import threading


def start_server(host='0.0.0.0', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    clients = []

    def broadcast(msg, exclude=None):
        for client in clients:
            if client is not exclude:
                try:
                    client.sendall(msg)
                except OSError:
                    pass

    def handle_client(conn, addr):
        with conn:
            clients.append(conn)
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    broadcast(data, exclude=conn)
            finally:
                clients.remove(conn)

    def _accept_loop():
        while True:
            conn, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            ).start()

    threading.Thread(target=_accept_loop, daemon=True).start()

    return server


def connect(host='localhost', port=5000, on_message=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    def listen():
        while True:
            data = client.recv(1024)
            if not data:
                break
            if on_message:
                on_message(data.decode('utf-8'))
    threading.Thread(target=listen, daemon=True).start()
    return client
