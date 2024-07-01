import socket
import threading
import json
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

PEDAZO_TAM = 102400  # 100 KB

def seleccionar_archivo():
    Tk().withdraw()  # Evita que aparezca una ventana vacía de Tkinter
    file_path = askopenfilename()  # Abre el cuadro de diálogo para seleccionar archivo
    return file_path

def calcular_hash(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

def cargar_torrent(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

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
        response = s.recv(1024).decode()
        return json.loads(response)

def obtener_peers(tracker_ip, tracker_port, torrent_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((tracker_ip, tracker_port))
        request = {
            "action": "get_peers",
            "torrent_id": torrent_id
        }
        s.send(json.dumps(request).encode())
        response = s.recv(1024).decode()
        return json.loads(response)["peers"]

def manejar_solicitud(conn, addr):
    try:
        request = json.loads(conn.recv(1024).decode())
        action = request.get("action")
        
        if action == "download_piece":
            index = request.get("index")
            with open(torrent_path, 'rb') as f:
                f.seek(index * PEDAZO_TAM)
                piece = f.read(PEDAZO_TAM)
            response = {
                "status": "success",
                "piece": piece.decode('latin1')  # Convertir bytes a cadena
            }
            conn.send(json.dumps(response).encode('latin1'))  # Convertir cadena a bytes
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
        threading.Thread(target=manejar_solicitud, args=(conn, addr)).start()

def descargar_pedazo(peer_ip, peer_port, index):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((peer_ip, peer_port))
        request = {
            "action": "download_piece",
            "index": index
        }
        s.send(json.dumps(request).encode())
        response = json.loads(s.recv(1024).decode('latin1'))
        if response.get("status") == "success":
            return response.get("piece").encode('latin1')  # Convertir cadena a bytes

def descargar_archivo(torrent_id, tracker_ip, tracker_port, client_ip, client_port, num_pieces):
    peers = obtener_peers(tracker_ip, tracker_port, torrent_id)
    if not peers:
        print("No se encontraron peers.")
        return
    
    os.makedirs("descargas", exist_ok=True)
    for peer in peers:
        peer_ip, peer_port = peer
        if (peer_ip, peer_port) != (client_ip, client_port):
            for index in range(num_pieces):
                piece = descargar_pedazo(peer_ip, peer_port, index)
                with open(f"descargas/{torrent_id}", "ab") as f:
                    f.write(piece)
            break

if __name__ == "__main__":
    # Seleccionar archivo torrent
    torrent_path = seleccionar_archivo()
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
