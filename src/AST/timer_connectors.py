import socket

def send_osr_command(command:str, socket_path:str) -> None:
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(socket_path)
            full_command:str = command+"\n"
            client.sendall(full_command.encode())
    except ConnectionRefusedError:
        print("Check if openspeedrun is running. the timer will have to be running for this to work")

def send_livesplit_command(command:str, host:str, port:int) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((host,port))
            full_command:str = command+"\n"
            client.sendall(full_command.encode())
    except ConnectionRefusedError:
        print("Check if Livesplit is running and Start Server is enabled")




def main() -> None:
    send_osr_command("start","/run/user/1000/openspeedrun.sock")

if __name__ == '__main__':
    main()
