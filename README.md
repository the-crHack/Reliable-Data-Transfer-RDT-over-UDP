# Reliable Data Transfer (RDT) over UDP

A Python implementation of reliable file transfer over UDP using packet sequencing, MD5 checksums, and selective acknowledgements. Since UDP provides no delivery guarantees, this project implements its own reliability layer on top of it.

## Overview

The client splits a file into numbered packets, each tagged with a 5-digit packet ID and an MD5 checksum. It sends all unacknowledged packets in a loop while a parallel thread listens for ACKs from the server. The server verifies each packet's checksum and sends back an ACK only for packets that arrive uncorrupted and in order. Transfer completes once all packets are acknowledged.

## Repository Structure
```
Reliable-Data-Transfer-RDT-over-UDP/
├── client.py    # Sender — splits file into packets and handles retransmission
└── server.py    # Receiver — reassembles file from packets with checksum verification
```

## How It Works

### Packet Format

Each packet sent over UDP is structured as:
```
[ 5-byte packet ID ][ 32-byte MD5 checksum ][ payload data ]
```

- **Packet ID** — zero-padded 5-digit sequence number (e.g., `00042`)
- **MD5 Checksum** — 32-character hex digest of the payload, used for corruption detection
- **Payload** — up to 8155 bytes of file data (buffer size 8192 minus 37 bytes of header)

### Client (`client.py`)

1. Prompts for the server IP and the file to send
2. Splits the file into fixed-size chunks and builds a dictionary of packets keyed by packet ID
3. Sends total packet count to the server before transfer begins
4. Spawns two threads:
   - **Sending thread** — continuously loops over unacknowledged packets and retransmits them
   - **ACK thread** — listens for ACK responses from the server and marks packets as acknowledged
5. Transfer ends when all packets are acknowledged

### Server (`server.py`)

1. Prompts for the IP address to bind to and listens on port `9999`
2. Receives the filename and total packet count from the client
3. For each incoming packet, verifies the MD5 checksum and sends back an ACK with the packet ID if valid
4. Ignores duplicate packets (already seen packet IDs)
5. Once all packets are received, reassembles them in order and writes the output file
6. Prints transfer statistics including throughput

## Requirements
```
Python 3.x
```

No external dependencies — uses only Python standard library (`socket`, `hashlib`, `threading`, `os`, `math`, `time`, `timeit`).

## Usage

Run the server and client in separate terminals, on the same machine or across a network.

### Step 1: Start the Server
```bash
python server.py
```

Enter the IP address of the machine running the server when prompted (e.g., `127.0.0.1` for localhost).

### Step 2: Start the Client
```bash
python client.py
```

Enter the same server IP address, then enter the path to the file you want to send.

### Example

**Server terminal:**
```
Enter IP address of server: 127.0.0.1
Server starting in 127.0.0.1...
Receiving File: sample.pdf
File Downloaded
No. of packets received: 412
No. of bytes received: 3363471
Time Taken: 4.23 s
Throughput:  777.45 kB/s
```

**Client terminal:**
```
Enter IP address of server: 127.0.0.1
Client connecting to 127.0.0.1...
Enter file u want to send: sample.pdf
Sending ...
Sent requested file
No. of packets sent: 438
No. of bytes sent: 3363471
```

## Notes

- Both client and server must be run from the same directory as the file being transferred, or use an absolute file path
- The server saves the received file with the same filename in its working directory
- Port `9999` is hardcoded — make sure it is not blocked by a firewall
- The small `time.sleep(0.0007)` delay between packets helps prevent UDP buffer overflow on the receiver side
