import sys
import socket
import getopt
import threading
import subprocess

#definindo algumas variáveis globais
listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0


#essa parte do código roda um comando e retorna a saída
def run_command(cmd):
    #remove a linha nova
    cmd = cmd.rstrip()

    try: 
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

    except subprocess.CalledProcessError as e:

        output = e.output

    return output

#lida com as conexões de entrada
def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        #lê todos os bytes e escreve no destino
        file_buffer = ''
        #permanece lendo os dados até que não haja mais nenhum disponível
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        #agora pegamos esses dados e tentamos escrevê-los
        try: 
            file_descriptor = open(upload_destination, 'wb')
            file_descriptor.write(file_buffer.encode('utf-8'))
            file_descriptor.close()

            client_socket.send('O arquivo foi salvo com sucesso em: %s\r\n' % upload_destination)
        except OSError:
            client_socket.send('Falha ao salvar o arquivo em: %s\r\n' % upload_destination)
    #verifica se é necessário executar um comando

    if len(execute):
        output = run_command(execute)

        client_socket.send(output)

    #agora vamos para outro loop se um shell de comando foi solicitado
    if command:
        while True:
            #exibe um prompt
            client_socket.send('<NetDog:#> '.encode('utf-8'))

            #agora recebemos dados até encontrar um enter (pressionar enter)

            cmd_buffer = b''
            while b'\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            #o comando dado foi valido, então vamos tentar executá-lo

            response = run_command(cmd_buffer.decode())

            #envia de volta a resposta
            client_socket.send(response)

        # essa parte do código lida com as conexões de entrada

def server_loop():
    global target
    global port

    #se o alvo não foi especificado, ouviremos todas as interfaces
    if not len(target):
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #dispara uma thread para cuidar do novo cliente
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

#se não ouvirmos, estaremos enviando dados de stdin
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #se conetar ao host alvo
        client.connect((target, port))
        #se um dado foi recebido, envia os dados, se não, espera o usuário digitar algo

        if len(buffer):
            client.send(buffer.encode('utf-8'))

        while True:
            #espera os dados de volta
            recv_len = 1
            response = b''

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response.decode('utf-8'), end=' ')

            #espera mais dados de entrada

            buffer = input('')
            buffer += '\n'

            #envia os dados
            client.send(buffer.encode('utf-8'))

    except socket.error as e:
        #tratamento de erro
        print('[*] Erro! Fechando a conexão.')
        print(f'[*] Erro: {e}')

        client.close()

def usage():
    print('#NetDog#')
    print()
    print('Uso: netdog.py -t target_host -p port')
    print('-l --listen - ouve novas conexões em [host]:[port]')
    print('-e --execute=file_to_run - executa um arquivo em uma conexão')
    print('-c --command - inicializa um comando shell')
    print('-u --upload=destination - upa um arquivo e escreve no [destino]')
    print()
    print()
    print('Exemplo: ')
    print('netdog.py -t 192.168.0.1 -p 5555 -l -c')
    print('netdog.py -t 192.168.0.1 -p 5555 -u=c:\\alvo.exe')
    print('netdog.py -t 192.168.0.1 -p 5555 -l -e=\'cat /etc/passwd\'')
    print('echo "ABCDEFGHI" | ./netdog.py -t 192.168.11.12 -p 135')
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # le as opçoes da linha de comando

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hle:t:p:cu:', ['help', 'listen', 'execute', 'target', 'port', 'command', 'upload'])

        for o, a in opts:
            if o in ('-h', '--help'):
                usage()
            elif o in ('-l', '--listen'):
                listen = True
            elif o in ('-e', '--execute'):
                execute = a
            elif o in ('-c', '--commandshell'):
                command = True
            elif o in ('-u', '--upload'):
                upload_destination = a
            elif o in ('-t', '--target'):
                target = a
            elif o in ('-p', '--port'):
                port = int(a)
            else:
                assert False, 'Opção Inválida'

    except getopt.GetoptError as err:
        print(str(err))
        usage()

    #aqui será dicidido se só vai ser ouvido ou enviado datos pelo STDIN
    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)
    if listen: 
        server_loop()

main()