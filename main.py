import socket
from rich.console import Console
from threading import Thread

console = Console()
serv = socket.socket()
cli = socket.socket()

clients = []

def listen_clients():
    while True:
        conn, addr = serv.accept()
        console.print(f"New connection: [green]{addr[0]}[/]")
        Thread(target=accept_client, args=(conn, addr)).start()

def accept_client(conn: socket.socket, addr):
    # conn.send(b"Hello")
    clients.append(conn)
    while True:
        data = conn.recv(1024)
        console.print(f"Data from [green]{addr[0]}[/]: {data}")
        for c in clients:
            c.send(data)

def client_input():
    while True:
        msg = console.input()
        if len(msg.strip()) == 0:
            continue
        cli.send(bytes(nickname, encoding="utf-8") + b"\x00" + bytes(msg, encoding="utf-8"))

def client_listen():
    while True:
        data = cli.recv(1024)
        console.print(f"Data from [blue]server[/]: {data}")
        split = data.split(b"\x00")
        name = str(split[0], encoding="utf-8")
        text = str(split[1], encoding="utf-8")
        console.print(f"[red]{name}[/]: {text}")

server_ip = ""
inp = console.input("Launch server [green]y[/]/[red]n[/] > ")
if inp == "y":
    serv.bind(("0.0.0.0", 2588))
    console.print("Listening at [yellow]0.0.0.0:2588[/]")
    serv.listen(255)
    Thread(target=listen_clients).start()
    server_ip = "127.0.0.1"
    nickname = input("Enter your nickname > ")
    cli.connect((server_ip, 2588))
else:
    nickname = input("Enter your nickname > ")
    while True:
        server_ip = console.input("Enter server ip > ")
        try:
            cli.connect((server_ip, 2588))
        except socket.gaierror as e:
            console.print("[red]Invalid ip[/]")
        except ConnectionRefusedError:
            console.print("[red]Connection refused[/]. Check if server is running and firewall isn't blocking port [yellow]2588[/]")
        except TimeoutError:
            console.print("[red]Connection timed out[/]. Check your network connection")
        break

Thread(target=client_input).start()
Thread(target=client_listen).start()