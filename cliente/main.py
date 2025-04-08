import socket
import os

HOST = '127.0.0.1'
PORT = 8181

def send_line(sock, msg):
    sock.sendall((msg + "\n").encode())

def read_line(sock):
    """Lê da conexão até encontrar '\n'."""
    line = b''
    while True:
        char = sock.recv(1)
        line += char
        if char == b'\n':
            break
    return line.decode().strip()

def enviar_arquivo(sock, caminho_arquivo):
    # Verifica se o arquivo existe
    if not os.path.isfile(caminho_arquivo):
        print(f"Arquivo {caminho_arquivo} não encontrado.")
        return

    with open(caminho_arquivo, "rb") as f:
        conteudo = f.read()
    tamanho = len(conteudo)
    nome_arquivo = os.path.basename(caminho_arquivo)
    
    # Envia o cabeçalho "FILE nome_arquivo tamanho"
    header = f"FILE {nome_arquivo} {tamanho}"
    send_line(sock, header)
    sock.sendall(conteudo)
    
    # Aguarda confirmação do servidor
    resposta = read_line(sock)
    print("Servidor:", resposta)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Aguardando autenticação com o HOST {HOST}, porta {PORT}")

    resposta = read_line(client_socket)
    if resposta != "AUTH_OK":
        print("Autenticação falhou. Resposta do servidor:", resposta)
        client_socket.close()
        return
    else:
        print("Autenticação realizada com sucesso.")
    
    arquivos = ["script1.py", "script2.sh"]
    for arq in arquivos:
        enviar_arquivo(client_socket, arq)
    
    send_line(client_socket, "QUIT")
    client_socket.close()

if __name__ == '__main__':
    main()
