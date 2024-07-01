import socket
import threading
import json

peers_db = {}

def handle_client(conn, addr):
    try:
        data = conn.recv(1024)
        if data:
            request = json.loads(data.decode())
            action = request.get("action")

            if action == "register":
                torrent_id = request.get("torrent_id")
                ip = request.get("ip")
                port = request.get("port")
                if torrent_id in peers_db:
                    peers_db[torrent_id].append((ip, port))
                else:
                    peers_db[torrent_id] = [(ip, port)]
                response = {"status": "success", "message": "Peer registrado"}
                conn.send(json.dumps(response).encode())
            
            elif action == "get_peers":
                torrent_id = request.get("torrent_id")
                peers = peers_db.get(torrent_id, [])
                response = {"status": "success", "peers": peers}
                conn.send(json.dumps(response).encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def start_tracker(server_ip, server_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)
    print(f"Tracker iniciado en {server_ip}:{server_port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker('127.0.0.1', 6881)
