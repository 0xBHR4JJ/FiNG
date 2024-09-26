import socket
import struct
import time
import os
import argparse
import asyncio


# ICMP constants
ICMP_ECHO_REQUEST = 8  # Type 8 for Echo Request

# Function to calculate checksum for ICMP packets
def checksum(source_string):
    sum = 0
    count = 0
    count_to = (len(source_string) // 2) * 2
    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xFFFFFFFF
        count = count + 2
    if count_to < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xFFFFFFFF
    sum = (sum >> 16) + (sum & 0xFFFF)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xFFFF
    answer = answer >> 8 | (answer << 8 & 0xFF00)
    return answer

# Function to create ICMP echo request packet
def create_packet(id):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = struct.pack('d', time.time())
    packet_checksum = checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(packet_checksum), id, 1)
    return header + data

# Function to send a single ICMP packet and receive a response (asynchronously)
async def ping_domain(domain, pid, timeout=1):
    try:
        # Resolve domain to IP
        ip = socket.gethostbyname(domain)
    except socket.gaierror:
        return None  # If domain resolution fails, return None

    # Create a raw socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print("You need to run this script as an administrator/root user.")
        return None

    # Create ICMP packet
    packet = create_packet(pid)

    # Send packet to the target IP address
    sock.sendto(packet, (ip, 1))
    start_time = time.time()

    # Set socket to non-blocking to use with asyncio
    sock.setblocking(False)
    
    # Wait for a reply
    while True:
        await asyncio.sleep(0.001)  # Yield control for a short time
        try:
            recv_packet, addr = sock.recvfrom(1024)
        except BlockingIOError:
            if time.time() - start_time > timeout:
                sock.close()
                return None  # Timed out
            continue

        # If packet is received, check ICMP header
        icmp_header = recv_packet[20:28]
        recv_type, code, checksum, recv_id, sequence = struct.unpack("bbHHh", icmp_header)

        if recv_id == pid:
            sock.close()
            return domain  # Successful ping

# Asynchronous function to handle multiple pings concurrently
async def ping_all_domains(domains):
    pid = os.getpid() & 0xFFFF  # Use process ID for packet ID

    # Use asyncio event loop to run pings concurrently
    tasks = [ping_domain(domain, pid) for domain in domains]
    results = await asyncio.gather(*tasks)
    return results

# Main function to handle argument parsing and start the pinging process
def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Ping domains faster than traditional ping.")
    parser.add_argument("-d", "--domain-file", required=True, help="Input file containing list of domains to ping.")
    parser.add_argument("-o", "--output-file", help="Output file to save active domains.")

    args = parser.parse_args()

    # Read domains from file if provided
    try:
        with open(args.domain_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File {args.domain_file} not found.")
        return

    # Start the asynchronous pinging process
    results = asyncio.run(ping_all_domains(domains))

    # Filter out None values (failed pings)
    active_domains = [domain for domain in results if domain]
    
    # Display the status of each domain on the screen
    for domain in domains:
        if domain in active_domains:
            print(f"\033[91m [FOUND]\033[0m {domain}")
        else:
            print(f"\033[91m [NOT FOUND]\033[0m {domain}")

    # If output file is provided, save only the active domains to it
    if args.output_file:
        with open(args.output_file, 'w') as f_out:
            for domain in active_domains:
                f_out.write(domain + "\n")
        print(f"Active domains written to {args.output_file}")


if __name__ == "__main__":
    print(""" 
  _____ _ _   _  ____ 
 |  ___(_) \ | |/ ___|
 | |_  | |  \| | |  _ 
 |  _| | | |\  | |_| |
 |_|   |_|_| \_|\____|
                      
                        - @0xBH4RJJ
     """)
    main()
