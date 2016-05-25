# Echo client program
import socket
import sys

def connect(host, port):
    s = None
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
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
        print "Error: Could not open socket on port " + port
        sys.exit(1)

    return s

if (len(sys.argv) == 5):
    HOST            = sys.argv[1]
    CONTROL_PORT    = sys.argv[2]
    COMMAND         = sys.argv[3]
    DATA_PORT       = sys.argv[4]
elif (len(sys.argv) == 6):
    HOST            = sys.argv[1]
    CONTROL_PORT    = sys.argv[2]
    COMMAND         = sys.argv[3]
    FILENAME        = sys.argv[4]
    DATA_PORT       = sys.argv[5]
else:
    print "Usage"

# Connect to control connection
control = connect(HOST, CONTROL_PORT)

# Send command
control.sendall(HOST + " " + COMMAND + " " + DATA_PORT)

# Response indicates on which connection to receive (control/data)
response = control.recv(1024)

# Receive on data connection
if response == "DATA":
    # Connect to data connection
    data = connect(HOST, DATA_PORT)
    response = data.recv(1024)
    # list
    if COMMAND == "-l":
        print "Receiving directory structure from " + HOST + ":" + DATA_PORT
        print response
    if COMMAND == "-g":
        print 'Receiving "' + FILENAME + '" from' + HOST + ":" + DATA_PORT
        print "File transfer complete"

# Close control connection
control.close()