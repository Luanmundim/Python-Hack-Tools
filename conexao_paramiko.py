import getpass
import subprocess
import paramiko


def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys('/home/justin/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024))
    client.close()
    return
def main():
    ip = input("Digite o IP do host: ")
    user = input("Digite o usuário: ")
    passwd = getpass.getpass("Digite a senha: ")
    command = input("Digite o comando: ")
    ssh_command(ip, user, passwd, command)


if __name__ == '__main__':
    main()




