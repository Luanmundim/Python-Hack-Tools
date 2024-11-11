import socket
import paramiko
import threading
import sys

# define as chaves
host_key = paramiko.RSAKey(filename= r'test_rsa.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if (username == 'root') and (password == 'toor'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print('[+] Esperando por conexões...')
    client, addr = sock.accept()
except Exception as e:
    print('[-] Falha ao escutar na porta: %d' % ssh_port)
    print('[-] Erro: %s' % str(e))
    sys.exit(1)
print('[+] Conexão recebida!')

try:
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException as x:
        print('[-] Falha ao iniciar o servidor SSH: %s' % str(x))
    chan = bhSession.accept(20)
    print('[+] Autenticado!')
    print(chan.recv(1024).decode())
    chan.send('Bem-vindo ao servidor SSH!')
    
    while True:
        try:
            command = input("Digite o comando: ").strip('\n')
            if command == '\n':
                break
            if command != 'exit':
                chan.send(command)
                print(chan.recv(1024).decode(errors="ignore") + '\n')
            else:
                chan.send('exit')
                print('[-] Encerrando a conexão...')
                bhSession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            print('[-] Cancelado pelo usuário...')
            bhSession.close()
finally:
    print('[+] Finalizando a conexão...')
    sys.exit(1)
