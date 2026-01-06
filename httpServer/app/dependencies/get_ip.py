import socket

def get_local_ip():
    try:
        # 连接到一个外部地址（不会实际发送数据）
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    print(get_local_ip())
