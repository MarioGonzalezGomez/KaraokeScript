import socket

HOST = '127.0.0.1'
PORT = 5000

print(f"🎧 Escuchando en {HOST}:{PORT}...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"✅ Conectado por {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                msg = data.decode('utf-8')
                print(f"📥 Recibido: {msg}")
            except:
                print(f"📥 Recibido (raw): {data}")
