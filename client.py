import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 12345
BUFSIZE = 64

def receive_and_save():
    file = open("received_video.ts","wb")
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFSIZE)
        except socket.timeout as e:
            break
        file.write(data)
    file.close()
if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1)
    video_path = input("Enter the path of the video file to send to the server: ")

    client_socket.sendto(video_path.encode(), (UDP_IP, UDP_PORT))

    print("Waiting for the server to send the converted video...")

    receive_and_save()
    print("morte")

    print("Video received and saved as 'received_video.ts'")
