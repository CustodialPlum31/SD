import tkinter as tk
from tkinter import filedialog
import socket
import json
import os
import hashlib
import threading

PEDAZO_TAM = 102400  # 100 KB

def calcular_hash(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

def registrar_torrent(tracker_ip, tracker_port, torrent_id, client_ip, client_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((tracker_ip, tracker_port))
        request = {
            "action": "register",
            "torrent_id": torrent_id,
            "ip": client_ip,
            "port": client_port
        }
        s.send(json.dumps(request).encode())
        response = json.loads(s.recv(1024).decode())
        return response

def obtener_peers(tracker_ip, tracker_port, torrent_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((tracker_ip, tracker_port))
        request = {
            "action": "get_peers",
            "torrent_id": torrent_id
        }
        s.send(json.dumps(request).encode())
        response = json.loads(s.recv(1024).decode())
        return response.get("peers", [])

def descargar_pedazo(ip, port, index):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        request = {
            "action": "get_piece",
            "index": index
        }
        s.send(json.dumps(request).encode())
        response = json.loads(s.recv(1024).decode())
        return response.get("piece")

def cargar_torrent(file_path):
    with open(file_path, 'r') as torrent_file:
        torrent_data = json.load(torrent_file)
    return torrent_data

def seleccionar_torrent():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir="torrents", title="Seleccionar Torrent",
                                           filetypes=(("Torrent files", "*.torrent"), ("all files", "*.*")))
    return file_path

def descargar_archivo(torrent_id, tracker_ip, tracker_port, client_ip, client_port, num_pieces):
    peers = obtener_peers(tracker_ip, tracker_port, torrent_id)
    if not peers:
        print("No se encontraron peers.")
        return
    
    # Descargar el archivo pieza por pieza
    for peer in peers:
        peer_ip, peer_port = peer
        if (peer_ip, peer_port) != (client_ip, client_port):
            for index in range(num_pieces):
                piece = descargar_pedazo(peer_ip, peer_port, index)
                # Guarda la pieza en el archivo
                with open(f"descargas/{torrent_id}", "ab") as f:
                    f.write(piece)
            break

def manejar_solicitud(conn):
    try:
        data = conn.recv(1024)
        if data:
            request = json.loads(data.decode())
            action = request.get("action")
            if action == "get_piece":
                index = request.get("index")
                # Leer la pieza del archivo correspondiente
                with open(f"archivos/{torrent_id}", "rb") as f:
                    f.seek(index * PEDAZO_TAM)
                    piece = f.read(PEDAZO_TAM)
                response = {
                    "status": "success",
                    "piece": piece.decode(errors='ignore')
                }
                conn.send(json.dumps(response).encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def iniciar_cliente(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)
    print(f"Cliente escuchando en {ip}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=manejar_solicitud, args=(conn,)).start()

if __name__ == "__main__":
    # Seleccionar archivo torrent
    torrent_path = seleccionar_torrent()
    if torrent_path:
        torrent_data = cargar_torrent(torrent_path)
        torrent_id = torrent_data['id']
        num_pieces = torrent_data['pieces']

        # Iniciar servidor del cliente para responder a solicitudes de piezas
        threading.Thread(target=iniciar_cliente, args=('127.0.0.1', 6882)).start()

        # Registrar torrent en el tracker
        response = registrar_torrent('127.0.0.1', 6881, torrent_id, '127.0.0.1', 6882)
        print(response)
        
        # Obtener peers del tracker
        peers = obtener_peers('127.0.0.1', 6881, torrent_id)
        print(peers)
        
        # Descargar archivo desde los peers
        descargar_archivo(torrent_id, '127.0.0.1', 6881, '127.0.0.1', 6882, num_pieces)
    else:
        print("No se seleccionó ningún archivo torrent.")
