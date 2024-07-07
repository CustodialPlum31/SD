import socket
import threading
import json

peers = {}

def handle_client(client_socket):
    request = json.loads(client_socket.recv(1024).decode('utf-8'))
    action = request.get('action')
    torrent_id = request.get('torrent_id')

    if action == 'register':
        ip = request.get('ip')
        port = request.get('port')
        if torrent_id not in peers:
            peers[torrent_id] = []
        peers[torrent_id].append((ip, port))
        response = {'status': 'success', 'message': 'Peer registrado'}
    elif action == 'get_peers':
        response = peers.get(torrent_id, [])
    else:
        response = {'status': 'error', 'message': 'Acción no válida'}

    client_socket.send(json.dumps(response).encode('utf-8'))
    client_socket.close()

def start_tracker(server_ip, server_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)
    print(f"Tracker escuchando en {server_ip}:{server_port}")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_tracker('127.0.0.1', 6881)
