"""
Nancy Chan
CS 372

Program 2

Source cited: https://docs.python.org/2/library/socket.html
"""

import socket
import sys

def initiateContact(host, port):
    """
    Create a socket given a host and port
    Supports both IPv4 and IPv6
    """
    s = None
    # Try to connect to all addresses returned as a result of the name resolution
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            # Socket call
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            s = None
            continue
        try:
            # Connect call
            s.connect(sa)
        except socket.error as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print "Error: Could not open socket on port " + port
        sys.exit(1)

    # Return socket
    return s

#----------------------------------------
# Main Program
#----------------------------------------

if len(sys.argv) == 5:
    HOST            = sys.argv[1]
    CONTROL_PORT    = sys.argv[2]
    COMMAND         = sys.argv[3]
    DATA_PORT       = sys.argv[4]
elif len(sys.argv) == 6:
    HOST            = sys.argv[1]
    CONTROL_PORT    = sys.argv[2]
    COMMAND         = sys.argv[3]
    FILENAME        = sys.argv[4]
    DATA_PORT       = sys.argv[5]
else:
    print "Usage: python " + sys.argv[0] + " <server host> <server port> <command: -l | -g filename> <data port>"
    exit(1)

# Connect to control connection
control = initiateContact(HOST, CONTROL_PORT)

# Send command
control.sendall(COMMAND)

# Confirm that server received command
response = control.recv(1024)

# Send command
if response == COMMAND:
    if COMMAND == "-l":
        control.sendall(HOST + " " + COMMAND + " " + DATA_PORT)
    if COMMAND == "-g":
        control.sendall(HOST + " " + COMMAND + " " + FILENAME + " " + DATA_PORT)

# Response indicates on which connection to receive (control/data)
response = control.recv(1024)

# Receive on data connection
if response == "DATA":
    # Connect to data connection
    data = initiateContact(HOST, DATA_PORT)
    response = data.recv(1024)
    # list
    if COMMAND == "-l":
        print "Receiving directory structure from " + HOST + ":" + DATA_PORT
        print response
    if COMMAND == "-g":
        print 'Receiving "' + FILENAME + '" from ' + HOST + ":" + DATA_PORT
        print "File transfer complete"

# Close control connection
control.close()