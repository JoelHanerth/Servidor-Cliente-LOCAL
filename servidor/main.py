import socket
import subprocess
import threading

HOST = ''      # Escuta em todas as interfaces
PORT = 8181

# Dados de autenticação
VALID_USER = "user"
VALID_PASS = "123"

def read_line(conn):
    """Lê da conexão até encontrar '\n' e retorna a linha (sem o terminador)."""
    line = b''
    while True:
        char = conn.recv(1)
        line += char
        if char == b'\n':
            break
    return line.decode().strip()

def handle_client(conn, addr):
    print("Conexão estabelecida com:", addr)
    
    # Autenticação (o formato esperado: "AUTH usuario senha")
    auth_line = read_line(conn)
    _, usuario, senha = auth_line.split()
    if usuario != VALID_USER or senha != VALID_PASS:
        conn.sendall("ERRO: autenticação falhou.\n".encode())
        conn.close()
        return
    else:
        conn.sendall("AUTH_OK\n".encode())
    
    while True:
        header = read_line(conn)
        if header.upper() == "QUIT":
            print("Cliente solicitou o fechamento da conexão.")
            break
        
        # Espera um cabeçalho no formato: "FILE nome_arquivo tamanho"
        _, nome_arquivo, tamanho_str = header.split()
        tamanho = int(tamanho_str)
        print(f"Recebendo arquivo: {nome_arquivo} ({tamanho} bytes)")
        
        # Recebe o conteúdo exato do arquivo
        recebido = b''
        while len(recebido) < tamanho:
            recebido += conn.recv(tamanho - len(recebido))
        
        # Salva o arquivo recebido
        with open(nome_arquivo, "wb") as f:
            f.write(recebido)
        print(f"Arquivo {nome_arquivo} salvo.")
        
        # Envia confirmação ao cliente
        conn.sendall(f"RECEBIDO {nome_arquivo}\n".encode())
        
        # Se o arquivo enviado for um shell script (.sh), executa-o imediatamente.
        if nome_arquivo.endswith(".sh"):
            print(f"Executando script shell: {nome_arquivo}")
            subprocess.run(["bash", nome_arquivo], timeout=30)
    
    conn.close()
    print("Conexão encerrada:", addr)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Servidor escutando em {HOST if HOST else 'localhost'}:{PORT}")
    
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    main()
