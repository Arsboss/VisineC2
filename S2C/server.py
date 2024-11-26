import socket, random
from threading import Thread
import web
import json

mode = "dev"
soc = None
TMSILIST = []
PMSILIST = {}

RQ_INITIAL_ALLOC_RESPONSE = "{RAND} Server running in {MODE} mode, allocated {IMSI}, required {ACTION}"


with open("./data/pmsi.txt") as f:
    for line in f:
        rest = line.split(":")
        PMSILIST.update({rest[0]: rest[1]})
  
if mode == "dev":  
    print("Running on staging pmsi list will be ignored and new hosts will get TMSI assigned instead.")
elif mode == "prod":
    print("Loaded permament imsi list: ", PMSILIST)
else:
    print("Invalid launch mode specified")

def setup_socket(host='0.0.0.0', port=12010):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

def udp_server(socket, host='0.0.0.0', port=12010):
    print(f"UDP server is running on {host}:{port}")
 
    while True:
        data, addr = socket.recvfrom(1024)
        message = data.decode('utf-8')

        #print(f"Received message: {message} from {addr}")
        
        if message == "keepalive":
            response = "proceeded"
            socket.sendto(response.encode('utf-8'), addr)
            print(f"Processed keepalive: {response} to {addr}")
        elif message == "initial":
            print(f"Processing initial request to {addr}")
            imsi = random.randint(100,999)
            if mode == "dev":
                response = RQ_INITIAL_ALLOC_RESPONSE.format(RAND=str(random.randint(100,9999999999999)), MODE=mode, IMSI=str(imsi), ACTION=None)
                TMSILIST.append(imsi)
                socket.sendto(response.encode('utf-8'), addr)
                data, addr = socket.recvfrom(1024)
                recvmessage = data.decode('utf-8')
                new_vm = {
                    f"{imsi}": {
                        "status": "online",
                        "lastKeepalive": "0",
                        "conn": f"{addr}"
                    }
                }

                with open("./data/sessions.txt", 'r+') as f:
                    oldjson = json.load(f)
                    f.seek(0)
                    oldjson["vms"].update(new_vm)
                    newjson = json.dumps(oldjson)
                    f.write(newjson)
                    f.close()

            print(f"Processed and added new host, IMSI: {imsi}, conn {addr}")
            
def udp_sendto_nowait(socket, host, port, message=''):
    socket.sendto(message.encode('utf-8'), (host, port))


def start_web():
    www = web.Web()
    www.start()

if __name__ == "__main__":
    setup_socket()
    udp_server_thread = Thread(target=udp_server, args=(sock,))
    udp_server_thread.start()
    start_web()
    
