import socket
import threading
import os

class HiddenArtifactServer:
    def __init__(self, ip="127.0.0.1", port=9999, file_dir="artifacts"):
        self.server_ip = ip
        self.server_port = port
        self.file_dir = file_dir
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

        # Cria o diretório de artefatos se não existir
        if not os.path.exists(self.file_dir):
            os.makedirs(self.file_dir)

        # Configuração do socket
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        print(f"[*] Servidor escutando em {self.server_ip}:{self.server_port}")

    def handle_client(self, client_socket, address):
        """Gerencia a comunicação com cada cliente."""
        print(f"[+] Nova conexão de {address[0]}:{address[1]}")
        client_socket.send(b"Bem-vindo ao servidor oculto de artefatos!\n")

        # Loop para manter a comunicação ativa
        while True:
            try:
                request = client_socket.recv(1024)
                if not request:
                    break
                command = request.decode('utf-8').strip()

                if command.startswith("download "):
                    # Extrai o nome do arquivo a partir do comando
                    _, filename = command.split(" ", 1)
                    response = self.send_file(client_socket, filename)
                    client_socket.send(response.encode('utf-8'))
                else:
                    client_socket.send(b"Comando não reconhecido.\n")
            except ConnectionResetError:
                print(f"[-] Conexão perdida com {address[0]}:{address[1]}")
                break

        client_socket.close()
        print(f"Conexão encerrada com {address[0]}:{address[1]}")
        self.clients.remove(client_socket)

    def send_file(self, client_socket, filename):
        """Envia o arquivo solicitado para o cliente."""
        filepath = os.path.join(self.file_dir, filename)
        if os.path.isfile(filepath):
            client_socket.send(b"Preparando o download...\n")
            with open(filepath, "rb") as f:
                # Lê e envia o arquivo em blocos de 1024 bytes
                while chunk := f.read(1024):
                    client_socket.send(chunk)
            return f"Arquivo '{filename}' enviado com sucesso.\n"
        else:
            return f"Arquivo '{filename}' não encontrado.\n"

    def run(self):
        """Método principal para rodar o servidor."""
        while True:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            client_handler.start()

# Execução do servidor
if __name__ == "__main__":
    # Inicializa o servidor na porta 9999 e com um diretório de artefatos chamado "artifacts"
    server = HiddenArtifactServer(ip="0.0.0.0", port=9999)
    server.run()
