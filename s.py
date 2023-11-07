import socket
import time
import os
import subprocess
from moviepy.editor import VideoFileClip
import re
import sys
# Configuração do servidor
VIDEO = "hls/1080_video0.ts"
DIR = '/hls'
BUFFER_SIZE = 65507 
MCAST_GRP = '224.1.1.1'  # IP Multicast
MCAST_PORT = 5007  # Porta Multicast
MULTICAST_TTL = 2

# Função para ordenar os arquivos ts
def extract_number(filename):
    parts = filename.split("video")
    if len(parts) > 1:
        number = int(parts[1].split(".")[0])
        return number

# Função para ler o vídeo
def read_video(filename):
    with open(filename, 'rb') as file:
        while True:
            data = file.read(BUFFER_SIZE - 4)  # 4 bytes reservados para o contador
            if not data:
                file.close()
                break
            yield data 

# Calcular o bitrate do vídeo
def get_video_bitrate(filename):
    cmd = ["ffmpeg", "-i", filename]
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = result.communicate()

    # Procura pelo bitrate no output do FFmpeg
    matches = re.search(r"bitrate: (\d+) kb/s", stdout.decode('utf-8'))
    if matches:
        return int(matches.group(1)) * 1000  # Converte kbps to bps

def get_bps(filename):
    bitrate = get_video_bitrate(filename)
    bytes_per_second = bitrate / 8
    return bytes_per_second

def main():
    # Definição dos sockets multicast
    timeSet = len(sys.argv)
    if timeSet>1:
        sleep_duration= float(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    counter = 0
    os.chdir("./hls")
    files = []
    bitrates = []
    log = open("../server.log", "w")
    log.write("Iniciando Transmissão\n")
    log.flush()
    # Itera sobre o diretório resgatando os nomes dos arquivos .ts
    try:
        while True:
            for filename in os.listdir('.'):
                if filename.endswith(".ts"):
                    files.append(filename)
            # Coloca os arquivos .ts em ordem
            files = sorted(files, key=extract_number)
            # Calcula o bitrate de cada arquivo
            for f in files:
                bitrates.append(get_bps(f))
            # Começa a transmissão
                for index, f in enumerate(files):
                    for data in read_video(f):
                        counter += 1
                        msg = counter.to_bytes(4, 'big') + data  # Prefix the data with the counter
                        log.write(f"Enviando o Pacote: {counter}\n")
                        log.flush()
                        sock.sendto(msg, (MCAST_GRP, MCAST_PORT))
                        if timeSet<2:
                            sleep_duration = len(data) / bitrates[index]
                        time.sleep(sleep_duration)
    except KeyboardInterrupt:
        log.write(f"Transmissão terminada com {counter} pacotes enviados\n")
        log.flush()
        log.close()

if __name__ == '__main__':
    main()
