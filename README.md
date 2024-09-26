# FiNG  
## Fast ICMP Ping Tool  
### A high-speed Python-based ICMP ping tool that uses asynchronous networking for faster domain availability checks.  

### Features  
High-Speed ICMP Requests: Uses asynchronous networking to handle multiple domains concurrently for faster results.  
Flexible Input Options: Accepts a single domain or a list of domains from a file (-d domain.txt).  
Output File: Save the domains that responded successfully to a specified file (-o active.txt).  
Root Permissions Required: Because it directly creates raw ICMP packets, the script must be run with administrative privileges.  

**Prerequisites**   
Python 3.x  
root privileges (to use raw sockets)  

### Usage:  
**1. Ping a Single Domain**  
If you want to ping a single domain and see if it responds:   
sudo python3 ping_tool.py example.com  
Output:  
`[FOUND] example.com`  


**2. Ping Multiple Domains from a File**  
To read a list of domains from a file and see the status of each:  
`sudo python3 ping_tool.py -d domain.txt`  
Output Example:  
`[FOUND] example.com`  
`[NOT FOUND] nonexistantdomain.com`  


**3. Save Active Domains to an Output File**  
You can save all the domains that respond successfully to an output file:  
`sudo python3 ping_tool.py -d domain.txt -o active.txt`  
Output:  
`[FOUND] example.com`  
`[NOT FOUND] nonexistantdomain.com`  
Active domains written to active.txt  
Only the [FOUND] domains will be saved to active.txt.  

**4. Example Domain File (domain.txt)**  
The input file should have one domain per line, like this:  
example.com  
nonexistantdomain.com  
anotherdomain.com  

**How It Works**  
The script sends ICMP echo requests to the specified domain(s) using raw sockets and waits for a response. It uses asynchronous programming (asyncio) to send and receive packets concurrently, making the process significantly faster than traditional synchronous ping commands.  

**Note**   
Running this script requires sudo or administrative privileges, as it uses raw sockets to send ICMP packets. If you receive a PermissionError, ensure that you are running it as a root user.


