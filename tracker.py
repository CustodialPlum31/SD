import socket
import threading
import json

peers = {}

def handle_client(conn, addr):
    data = conn.recv(1024).decode()
    request = json.loads(data)
    action = request.get('action')

    if action == 'register':
        torrent_id = request['torrent_id']
        client_ip = request['client_ip']
        client_port = request['client_port']
        
        if torrent_id not in peers:
            peers[torrent_id] = []
        
        peer_info = (client_ip, client_port)
        if peer_info not in peers[torrent_id]:
            peers[torrent_id].append(peer_info)
        
        response = {'status': 'success', 'message': 'Peer registrado'}
        conn.sendall(json.dumps(response).encode())

    elif action == 'get_peers':
        torrent_id = request['torrent_id']
        response = {'peers': peers.get(torrent_id, [])}
        conn.sendall(json.dumps(response).encode())

    conn.close()

def start_tracker(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)
    print(f"Tracker iniciado en {ip}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker('127.0.0.1', 6881)
