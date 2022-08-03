import socket
import os
import math
import time
import threading
import hashlib

# HOST = ""
HOST = input("Enter IP address of server: ")
# HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999
BUFFER_SIZE = 8192
FORMAT = 'utf-8'
ADDR = (HOST, PORT)

packets_dict = {}
ack = []
sent_packets = 0 
total_packets = 0
packets = 0

client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

def sending():
    global packets
    i = 0
    while (sent_packets < total_packets):
        i += 1
        pid = 0
        for pid in range(total_packets):
            if ack[pid] == 0:
                client.sendto(packets_dict[pid], ADDR)
                time.sleep(0.0007)
                packets += 1
        print(f"Successful packets sent after {i} iteration: {sent_packets}")

def acknowledgement():
    global sent_packets
    while (sent_packets < total_packets):
        data, addr = client.recvfrom(BUFFER_SIZE)
        ind = int(data.decode(FORMAT))
        if ack[ind] == 0:
            ack[ind] = 1
            sent_packets += 1

print(f"Client connecting to {HOST}...")

while True:

    file_name = input("Enter file u want to send: ")

    client.sendto(file_name.encode(FORMAT),ADDR)

    if not os.path.exists(file_name):
        print("File doesn't exist")
        continue

    file_size = os.path.getsize(file_name)
    total_packets = math.ceil(file_size / 8155)

    for i in range(total_packets):
        ack.append(0)

    string = str(total_packets)
    client.sendto(string.encode(FORMAT), ADDR)

    f=open(file_name,"rb")
    data = f.read(BUFFER_SIZE - 37)
    p_id = 0
    packets = 0
    while (data):
        str_pid = str(p_id)
        str_pid = '0' * (5 - len(str_pid)) + str_pid
        checksum = (hashlib.md5(data).hexdigest()).encode(FORMAT)
        data = str_pid.encode(FORMAT) + checksum + data
        packets_dict[p_id] = data
        data = f.read(BUFFER_SIZE-37)
        p_id += 1

    print(len(packets_dict.keys()))
    print ("Sending ...")

    send_thread = threading.Thread(target = sending)
    ack_thread = threading.Thread(target = acknowledgement)

    send_thread.start()
    ack_thread.start()

    send_thread.join()
    ack_thread.join()

    print("Sent requested file")
    print(f"No. of packets sent: {packets}")
    print(f"No. of bytes sent: {file_size}")
    f.close()
    break
