import hashlib
import os
import json
from tkinter import Tk, filedialog

PEDAZO_TAM = 102400  # 100 KB

#Funcion para calcular el hash md5
def calcular_hash(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()



def crear_torrent(file_path, tracker_ip, tracker_port):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    pieces = []
    
    with open(file_path, 'rb') as f:
        while True:
            piece = f.read(PEDAZO_TAM)
            if not piece:
                break
            pieces.append(calcular_hash(piece))
    
    torrent_data = {
        'id': calcular_hash(file_name.encode()),
        'tracker': tracker_ip,
        'puertoTracker': tracker_port,
        'pieces': len(pieces),
        'lastPiece': len(piece),
        'name': file_name,
        'filepath': file_path,
        'checksum': pieces
    }
    
    torrent_file_name = f"torrents/{file_name}.torrent"
    with open(torrent_file_name, 'w') as torrent_file:
        json.dump(torrent_data, torrent_file, indent=4)
    
    print(f"Torrent creado: {torrent_file_name}")

def seleccionar_archivo():
    root = Tk()
    file_path = filedialog.askopenfilename(title="Selecciona un archivo")
    return file_path

if __name__ == "__main__":
    file_path = seleccionar_archivo()
    if file_path:
        tracker_ip = 'localhost'  # Cambia esto a la IP de tu tracker
        tracker_port = 5000 # Cambia esto al puerto de tu tracker
        crear_torrent(file_path, tracker_ip, tracker_port)
    else:
        print("No se seleccionó ningún archivo")
