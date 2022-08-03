import socket
import os
import time
import timeit
import hashlib

# HOST = socket.gethostbyname(socket.gethostname())
# HOST = ""
HOST = input("Enter IP address of server: ")
PORT = 9999

file_dict = {}

server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.bind((HOST, PORT))

BUFFER_SIZE = 8192
FORMAT = 'utf-8' 

print(f"Server starting in {HOST}...")

while True:

    data,addr = server.recvfrom(BUFFER_SIZE)
    fn = data.strip()
    print(fn.decode(FORMAT))

    packets = 0
    
    start = timeit.default_timer()

    data,addr = server.recvfrom(BUFFER_SIZE)
    total_packets = int(data.decode(FORMAT))

    data,addr = server.recvfrom(BUFFER_SIZE)

    print ("Receiving File:",fn.decode(FORMAT))
    f = open(fn.decode(FORMAT),'wb')

    while packets < total_packets:
        p_id = int(data[:5])
        cksum = data[5:37]
        data = data[37:]
        
        cksum1 = (hashlib.md5(data).hexdigest()).encode('utf-8')
        
        if cksum == cksum1:
 	
            if p_id not in file_dict.keys():
                packets += 1

            file_dict[p_id] = data
            server.sendto(str(p_id).encode(FORMAT), addr)
            time.sleep(0.0007)
            
            if packets >= total_packets:
                break
        server.settimeout(1000)
        data,addr = server.recvfrom(BUFFER_SIZE)
    stop = timeit.default_timer()

    for i in range(len(file_dict.keys())):
        f.write(file_dict[i])
    f.close()
    print ("File Downloaded")
    time_taken = stop - start
    size = os.path.getsize(fn)

    print(f"No. of packets received: {len(file_dict.keys())}")
    print(f"No. of bytes received: {size}")
    print(f"Time Taken: {time_taken} s")
    print(f"Throughput: {(size/time_taken)/1024: .2f} kB/s")
    break
