# Echo client program
import socket
import sys

HOST            = sys.argv[1]
CONTROL_PORT    = sys.argv[2]
COMMAND         = sys.argv[3]
DATA_PORT       = sys.argv[4]

s = None
for res in socket.getaddrinfo(HOST, CONTROL_PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print 'could not open socket'
    sys.exit(1)
s.sendall(COMMAND + " " + DATA_PORT)
data = s.recv(1024)
s.close()

if COMMAND == "-l":
    print 'Receiving directory structure from ' + HOST + ':' + DATA_PORT;

print data