import socket
import threading
import json
import time

def select_torrent_file():
    # Implementa la lógica para seleccionar un archivo .torrent
    return "ruta/al/archivo.torrent"

def load_torrent_info(path):
    # Implementa la lógica para cargar la información del archivo .torrent
    return {
        'id': 'ejemplo-torrent-id',
        'pieces': 5
    }

# Peers simulados para cada cliente (pueden ser diferentes puertos en la misma IP)
SIMULATED_PEERS = [('127.0.0.1', 6884), ('127.0.0.1', 6885)]

def register_torrent(tracker_ip, tracker_port, torrent_id, client_ip, client_port):
    # Simulamos el registro exitoso en el tracker
    response = {'status': 'success', 'message': 'Peer registrado'}
    return response

def get_peers(tracker_ip, tracker_port, torrent_id):
    # Simulamos obtener la lista de peers del tracker
    return SIMULATED_PEERS

def handle_request(conn):
    data = conn.recv(1024).decode()
    request = json.loads(data)
    if request['action'] == 'get_piece':
        index = request['index']
        # Aquí puedes simular la respuesta con datos de la pieza
        piece_data = f"Datos del pedazo {index}".encode()
        conn.sendall(piece_data)
    conn.close()

def start_client(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)
    print(f"Cliente escuchando en {ip}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_request, args=(conn,)).start()

def download_file(torrent_id, tracker_ip, tracker_port, client_ip, client_port, num_pieces):
    print("Obteniendo peers simulados...")
    peers_list = get_peers(tracker_ip, tracker_port, torrent_id)
    print("Peers simulados obtenidos:", peers_list)

    # Descargar desde el primer peer simulado
    if peers_list:
        peer_ip, peer_port = peers_list[0]
        if (peer_ip, peer_port) != (client_ip, client_port):
            print(f"Conectando con peer simulado: {peer_ip}:{peer_port}")
            for index in range(num_pieces):
                print(f"Descargando pedazo {index} desde {peer_ip}:{peer_port}")
                # Simulación de descarga de pedazo
                time.sleep(1)  # Simulación de tiempo de descarga
                print(f"Pedazo {index} descargado.")
            print("Archivo descargado completamente.")
        else:
            print(f"Saltando el peer simulado {peer_ip}:{peer_port} porque es el mismo cliente.")

if __name__ == "__main__":
    torrent_path = select_torrent_file()
    if torrent_path:
        torrent_info = load_torrent_info(torrent_path)
        torrent_id = torrent_info['id']
        num_pieces = torrent_info['pieces']

        threading.Thread(target=start_client, args=('127.0.0.1', 6885)).start()

        response = register_torrent('127.0.0.1', 6881, torrent_id, '127.0.0.1', 6883)
        print(response)

        download_file(torrent_id, '127.0.0.1', 6881, '127.0.0.1', 6883, num_pieces)
    else:
        print("No se seleccionó ningún archivo torrent.")
