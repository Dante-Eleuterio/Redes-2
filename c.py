import socket
import subprocess
import struct
import logging
# Configuration
BUFFER_SIZE = 65507
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
def receive_data(sock, buffer, last_counter,out_order_packets,lost_packets):
    #Abre o VLC para streamar o vídeo
    player = subprocess.Popen(["vlc", "fd://0"], stdin=subprocess.PIPE)
    log = open("clientLog.log", "w")
    timeout=0
    while True:
        data, _ = sock.recvfrom(BUFFER_SIZE)
        counter = int.from_bytes(data[:4], 'big')
        #Caso seja o primeiro pacote recebido
        if last_counter == 0:
            last_counter = counter
            player.stdin.write(data[4:])
            log.write(f"Recebi o Pacote: {counter}\n")
            log.flush()
        else:
            #Se é o pacote esperado
            if counter == last_counter + 1:
                if len(buffer)>0:
                    out_order_packets+=1
                timeout=0
                player.stdin.write(data[4:])
                log.write(f"Recebi o Pacote: {counter}\n")
                log.flush()
                last_counter += 1
                #Percorre o buffer de pacotes fora de ordem os escrevendo e contabiliza o número de pacotes perdidos
                while len(buffer)>0:
                        if last_counter+1 in buffer:
                            while last_counter + 1 in buffer:
                                player.stdin.write(buffer[last_counter + 1])
                                log.write(f"Recebi o Pacote: {counter}\n")
                                log.flush()
                                del buffer[last_counter + 1]
                                last_counter += 1
                        else:
                            last_counter+=1
                            lost_packets+=1
            else:
                #Caso tenha estourado o número de tentativas de receber o pacote certo
                if timeout==10:
                    timeout=0
                    lost_packets+=1
                    #Percorre o buffer de pacotes fora de ordem os escrevendo e contabiliza o número de pacotes perdidos
                    while len(buffer)>0:
                        if last_counter+1 in buffer:
                            while last_counter + 1 in buffer:
                                player.stdin.write(buffer[last_counter + 1])
                                log.write(f"Recebi o Pacote: {counter}\n")
                                log.flush()

                                del buffer[last_counter + 1]
                                last_counter += 1
                        else:
                            last_counter+=1
                            lost_packets+=1
                else:
                    timeout+=1
                    out_order_packets+=1
                    buffer[counter] = data[4:]

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    last_counter = 0
    out_order_packets=0
    lost_packets=0
    buffer = {}
    receive_data(sock,buffer,last_counter,out_order_packets,lost_packets)
    sock.close()
if __name__ == '__main__':
    main()
