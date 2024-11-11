import sys
import socket
import threading

# this is a pretty hex dumping function directly taken from
# http://code.activestate.com/recipes/142812-hex-dumper/

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i:i + length]
        hexa = b' '.join([b"%0*X" % (digits, ord(chr(x))) for x in s])
        text = b''.join([bytes(x) if 0x20 <= ord(chr(x)) < 0x7F else b'.' for x in s])
        result.append(
            b"%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))

    print(b'\n'.join(result))


def receive_from(connection):
    buffer = b''
    #foi setados dois segundos de timeout; dependendo do alvo, você pode ter que ajustar esse valor
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except TimeoutError:
        pass
    return buffer

def request_handler(buffer):
    #faça modificações no pacote
    return buffer

def response_handler(buffer):
    #faça modificações no pacote
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    #conecta-se ao host remoto
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    #recebe dados do lado remoto se necessário
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        #envia os dados para a nossa função de resposta
        if len(remote_buffer):
            print("[<==] Enviando %d bytes para o locahost." % len(remote_buffer))
            client_socket.send(remote_buffer)


    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print("[==>] Recebido %d bytes do host remoto" % len(local_buffer))
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Enviado ao host remoto.")
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Recebido %d bytes do host remoto." % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Enviado ao localhost.")

        #if not len(local_buffer) or not len(remote_buffer):
        #    client_socket.close()
        #    remote_socket.close()
        #    print("[*] Sem dados, encerrando a conexão.")
        #    break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except socket.error as msg:
        print("[!!] Falha ao escutar em %s:%d. Erro: %s" % (local_host, local_port, msg))
        print("[!!] Verifique se a porta %d não está em uso" % local_port)
        sys.exit(0)

    print("[*] Escutando em %s:%d" % (local_host, local_port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        #imprime informações sobre a conexão local
        print("[==>] Recebida conexão de %s:%d" % (addr[0], addr[1]))
        #inicia uma thread para conversar com o host remoto
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()
def main():
    if len(sys.argv[1:]) != 5:
        print("Uso: ./tcp_proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Exemplo: ./tcp_proxy.py 127.0.0.1 9000 20.12.132.1 9000 True")
        sys.exit(0)

    #configuração dos parâmetros
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    #diz ao nosso proxy para conectar e receber dados antes de enviar ao host remoto
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
if __name__ == '__main__':
    main()