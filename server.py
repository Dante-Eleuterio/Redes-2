import socket
import threading
import subprocess
import os
UDP_IP = "127.0.0.1"
UDP_PORT = 12345
BUFSIZE = 64

def convert_and_send(video_path, client_address):
    try:
        output_path="output.ts"
        subprocess.run(['ffmpeg', '-i', video_path, '-c', 'copy', '-bsf:v', 'h264_mp4toannexb', '-f', 'mpegts', output_path], check=True)
        with open(output_path, 'rb') as file:
            data = file.read(BUFSIZE)
            while data:
                server_socket.sendto(data, client_address)
                data = file.read(BUFSIZE)
        os.remove(output_path)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((UDP_IP, UDP_PORT))

    print("Server listening on {}:{}".format(UDP_IP, UDP_PORT))

    # while True:
    data, client_address = server_socket.recvfrom(BUFSIZE)
    video_path = data.decode()
    convert_and_send(video_path,client_address)
    # threading.Thread(target=convert_and_send, args=(video_path, client_address)).start()