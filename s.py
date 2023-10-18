import socket
import time
import pickle

# Configuração do servidor
VIDEO = "hls/1080_video16.ts"
BUFFER_SIZE = 65507  # MTU IPV4 - 20 (IP header) - 8 (UDP header)
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
MULTICAST_TTL = 2

def read_video(filename):
    with open(filename, 'rb') as file:
        while True:
            data = file.read(BUFFER_SIZE - 4)  # 4 bytes reserved for the counter
            if not data:
                file.close()
                break
            yield data

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    counter=0
    input("batata")
    while True:
        print("começando")
        for data in read_video(VIDEO):
            counter += 1
            msg = counter.to_bytes(4, 'big') + data  # Prefix the data with the counter
            sock.sendto(msg, (MCAST_GRP, MCAST_PORT))
            time.sleep(0.1)

if __name__ == '__main__':
    main()