import socket
import subprocess
import struct
# Configuration
BUFFER_SIZE = 65507
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

def receive_data(sock, buffer, last_counter):
    player = subprocess.Popen(["vlc", "fd://0"], stdin=subprocess.PIPE)
    while True:
        data, _ = sock.recvfrom(BUFFER_SIZE)
        counter = int.from_bytes(data[:4], 'big')
        if last_counter == 0:
            last_counter = counter
            player.stdin.write(data[4:])
        else:
            if counter == last_counter + 1:
                player.stdin.write(data[4:])
                last_counter += 1

                while last_counter + 1 in buffer:
                    player.stdin.write(buffer[last_counter + 1])
                    del buffer[last_counter + 1]
                    last_counter += 1
            else:
                buffer[counter] = data[4:]

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    last_counter = 0
    buffer = {}
    receive_data(sock,buffer,last_counter)
    sock.close()
if __name__ == '__main__':
    main()
