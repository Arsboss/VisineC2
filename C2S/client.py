import socket, time, re
from threading import Thread

dsthost = '127.0.0.1'
dstport = 12010
sock = None
TMSI = None
PMSI = None

regex_matches_mode = "(?<=running in\s)(\w+)(?=\smode)"
regex_matches_required_action = "(?<=required\s).*"
regex_groups_imsi = "allocated\s+(\S+),"

def setup_socket(srcport):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", srcport))

def udp_sendto_nowait(socket, host, port, message=''):
    socket.sendto(message.encode('utf-8'), (host, port))
        
def udp_sendto_action(socket, host, port, action=''):
    socket.sendto(action.encode('utf-8'), (host, port))
    if action == "keepalive":
        data, _ = socket.recvfrom(1024)
        print(f"Received keepalive from server: {data.decode('utf-8')}")
    elif action == "initial":
        data, _ = socket.recvfrom(1024)
        data.decode('utf-8')
        stringdata = str(data)
        
        ssmode = re.findall(regex_matches_mode, stringdata)[0]
        ssreimsi = re.search(regex_groups_imsi, stringdata)
        ssimsi = ssreimsi.group(1)
        required_action = re.findall(regex_matches_required_action, stringdata)[0]

        udp_sendto_nowait(socket, host, port, "172.16.1.0")
        print(f"Got allocation, c2 server is in {ssmode} mode, IMSI: {ssimsi}, required action: {required_action}")
        
def keepalive_conn(socket, host, port):
    while True:
        udp_sendto_action(sock, dsthost, dstport, action="keepalive")
        time.sleep(19)
        
def socket_listeting(socket):
    while True:
        data = socket.recv(1024)
        print("Received data from server:", data)
    
if __name__ == "__main__":
    setup_socket(57758)
    udp_sendto_action(sock, dsthost, dstport, action="initial")
    keepalive_thread = Thread(target=keepalive_conn, args=(sock, dsthost, dstport,))
    keepalive_thread.start()
    socket_listeting_thread = Thread(target=socket_listeting, args=(sock,))
    socket_listeting_thread.start()