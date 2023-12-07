import socket

udp_ip = "127.0.0.1"  # Unity运行在同一台计算机上时，可以使用本地回环地址
udp_port = 34568  # 与Unity接收端使用相同的端口

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def listen(server_socket, PORT):
    HOST = '127.0.0.1'  # 服務器IP地址

    # 开始监听连接
    server_socket.listen()
    sock.sendto("ready".encode(), (udp_ip, udp_port))

    print(f"等待Unity連接在 {HOST}:{PORT} 上...")

    # 接受连接
    client_socket, addr = server_socket.accept()
    print(f"連接來自 {addr}")

    while True:
        data = client_socket.recv(1024)  # 接收數據
        if not data:
            break
        message = data.decode('utf-8')  # 解碼數據
        print(f"从Unity接收到的消息: {message}")
        if message == "true":
            return True
        if message == "switch":
            return message

        # 在這裡執行其他操作，如果需要的話

    client_socket.close()