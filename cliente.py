import socket
import threading
import json
import os

piece_size = 1024

if not os.path.exists('descargas'):
    os.makedirs('descargas')

def cargar_torrent(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def seleccionar_archivo():
    torrents = os.listdir('torrents')
    print("Archivos torrent disponibles:")
    for i, torrent in enumerate(torrents):
        print(f"{i + 1}. {torrent}")
    seleccion = int(input("Selecciona un archivo torrent (número): "))
    return os.path.join('torrents', torrents[seleccion - 1])

def registrar_torrent(tracker_ip, tracker_port, torrent_id, client_ip, client_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tracker_ip, tracker_port))
    request = {
        'action': 'register',
        'torrent_id': torrent_id,
        'ip': client_ip,
        'port': client_port
    }
    s.send(json.dumps(request).encode('utf-8'))
    response = s.recv(1024).decode('utf-8')
    s.close()
    return json.loads(response)

def obtener_peers(tracker_ip, tracker_port, torrent_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tracker_ip, tracker_port))
    request = {
        'action': 'get_peers',
        'torrent_id': torrent_id
    }
    s.send(json.dumps(request).encode('utf-8'))
    response = s.recv(1024).decode('utf-8')
    s.close()
    return json.loads(response)

def iniciar_cliente(client_ip, client_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((client_ip, client_port))
    server.listen(5)
    print(f"Cliente escuchando en {client_ip}:{client_port}")

    def handle_peer(conn, addr):
        piece_index = conn.recv(1024).decode('utf-8')
        file_path = f"descargas/{torrent_id}"

        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(b"\0" * (num_pieces * piece_size))  # Crear un archivo vacío con el tamaño total

        with open(file_path, "rb") as f:
            f.seek(int(piece_index) * piece_size)
            piece_data = f.read(piece_size)
        conn.send(piece_data)
        conn.close()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_peer, args=(conn, addr)).start()

def descargar_pedazo(peer_ip, peer_port, piece_index):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((peer_ip, peer_port))
    s.send(str(piece_index).encode('utf-8'))
    piece_data = s.recv(piece_size)
    s.close()
    return piece_data

def descargar_archivo(torrent_id, tracker_ip, tracker_port, client_ip, client_port, num_pieces):
    peers = obtener_peers(tracker_ip, tracker_port, torrent_id)
    for peer in peers:
        peer_ip, peer_port = peer
        if (peer_ip, peer_port) != (client_ip, client_port):
            print(f"Conectando con peer: {peer}")
            for index in range(num_pieces):
                piece = descargar_pedazo(peer_ip, peer_port, index)
                with open(f"descargas/{torrent_id}", "r+b") as f:
                    f.seek(index * piece_size)
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
        threading.Thread(target=iniciar_cliente, args=('127.0.0.1', 6885)).start()

        # Registrar torrent en el tracker
        response = registrar_torrent('127.0.0.1', 6881, torrent_id, '127.0.0.1', 6885)
        print(response)

        # Obtener peers del tracker
        peers = obtener_peers('127.0.0.1', 6881, torrent_id)
        print("Obteniendo peers...")
        print(f"Peers obtenidos: {peers}")

        # Descargar archivo desde los peers
        descargar_archivo(torrent_id, '127.0.0.1', 6881, '127.0.0.1', 6885, num_pieces)
    else:
        print("No se seleccionó ningún archivo torrent.")
