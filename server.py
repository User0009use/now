import socket
import ssl
import select

class Log:
    def suc(self, msg):
        print(f"\033[1;32m{msg}\033[m")
    def info(self, msg):
        print(f"\033[1;34m{msg}\033[m")
    def error(self, msg):
        print(f"\033[1;31m{msg}\033[m")

logging = Log()
HOST = ""
PORT = 8080

def start_proxy(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    logging.info(f"Proxy rodando em {socket.gethostbyname(socket.gethostname())}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        logging.suc(f">>> Conexão de {addr}")
        handle_client(client_socket)

def handle_client(client_socket):
    request = client_socket.recv(4096).decode()
    logging.info(f"\t> Solicitação recebida:\n{request}".replace("\n","\n\t"))

    lines = request.splitlines()
    if len(lines) > 0:
        first_line = lines[0].split()
        method = first_line[0]
        url = first_line[1]

        if method == 'CONNECT':
            # Tratamento especial para solicitações CONNECT
            host, port = url.split(':')
            port = int(port)
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                target_socket.connect((host, port))

                # Responder com uma mensagem de resposta HTTP
                client_socket.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                # Encaminhar os dados entre o cliente e o servidor de destino
                _read_write(client_socket, target_socket)
            except socket.gaierror:
                logging.error(f"Erro ao conectar com o host: {host}")
                client_socket.send(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                client_socket.close()

        else:
            # Determinar se é HTTP ou HTTPS
            if url.startswith("http://"):
                url = url[7:]  # Remove 'http://'
                port = 80
            elif url.startswith("https://"):
                url = url[8:]  # Remove 'https://'
                port = 443
            else:
                client_socket.close()
                return

            host, path = (url.split('/', 1) + [''])[:2]

            try:
                # Conectar ao servidor de destino
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_socket.connect((host, port))
                if port == 443:  # Para HTTPS, envolva em SSL
                    target_socket = ssl.wrap_socket(target_socket)
                    
                # Enviar a requisição ao servidor de destino
                target_socket.send(f"{method} /{path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())

                # Receber a resposta do servidor de destino
                response = b""
                while True:
                    chunk = target_socket.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                target_socket.close()

                # Enviar a resposta de volta ao cliente
                client_socket.send(response)
            except socket.gaierror:
                logging.error(f"Erro ao conectar com o host: {host}")
                client_socket.send(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
    
    client_socket.close()

def _read_write(client_socket, target_socket):
    socs = [client_socket, target_socket]
    count = 0
    while 1:
        count += 1
        (recv, _, error) = select.select(socs, [], socs, 3)
        if error:
            break
        if recv:
            for in_ in recv:
                data = in_.recv(4096)
                if in_ is client_socket:
                    out = target_socket
                else:
                    out = client_socket
                if data:
                    out.send(data)
                    #print(len(data))
                    count = 0
        print("... > ", count)
        if count == 1: #time_out_max
            break
    target_socket.close()
    client_socket.close()

def tunnel_connection(client_socket, target_socket):
    while True:
        try:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            target_socket.send(chunk)
        except socket.error:
            break
    target_socket.close()
    client_socket.close()


class Main:
    def __init__(self) -> None:
        self.host = ""
        self.port = 8080

    def run(self, *args, **kwargs):
        print(*args)
        print(**kwargs)
        start_proxy(self.host, self.port)

app = Main()

if __name__ == "__main__":
    app.run(HOST, PORT)