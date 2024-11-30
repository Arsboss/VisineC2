# VisineC2

This is a very first prototype of remote access program that i used to install on my school boards lul :D
Передаем привет сис админу который вместо того что бы поменять одной командой настры arp тупо офнул весь study mos

## How to install?
The S2C folder is the server. All you need to do is install Flask and run server.py file, it's all done.\
```
pip3 install flask
python3 server.py
```
On the client (aka the remote machine you want to control) just launch client.py from C2S folder. 
> Don't forget to change the server ip in dsthost variable
```
python3 client.py
```