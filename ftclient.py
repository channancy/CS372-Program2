"""
Nancy Chan
CS 372

Program 2

Sources cited:
https://docs.python.org/2/library/socket.html
"""

import socket
import sys

def initiateContact(host, port):
    """
    Create a socket given a host and port
    Connect to the socket
    Both IPv4 and IPv6 are supported
    """
    s = None

    # Try to connect to all addresses returned as a result of the name resolution
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        
        # Socket call
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            s = None
            continue
        
        # Connect call
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

    # Return socket
    return s

def makeRequest():
    """
    Send a request to server
    """
    # Send command
    control.sendall(COMMAND)

    # Confirm that server received command
    response = control.recv(1024)

    # Send details of command
    if response == COMMAND:
        if COMMAND == "-l":
            control.sendall(HOST + " " + COMMAND + " " + DATA_PORT)
        if COMMAND == "-g":
            control.sendall(HOST + " " + COMMAND + " " + FILENAME + " " + DATA_PORT)

def receiveFile():
    """
    Receive requested file from server
    """
    # Receive file size
    filesize = int(control.recv(1024))

    # Initialize variables to be concatenated/incremented
    filecontents = ""
    bytes_sent_total = 0

    print 'Receiving "' + FILENAME + '" from ' + HOST + ":" + DATA_PORT

    # Receive file contents in increments of 1000 until reach file size
    while bytes_sent_total < filesize:
        filecontents += data.recv(1000)
        bytes_sent_total += 1000

    # Create a file
    fo = open(FILENAME, 'wb')

    # Write file contents to file
    fo.write(filecontents)

    print "File transfer complete"

#----------------------------------------
# Main Program
#----------------------------------------

# Check command line arguments
# Length of 5 means filename not included
if len(sys.argv) == 5:
    HOST            = sys.argv[1]
    CONTROL_PORT    = sys.argv[2]
    COMMAND         = sys.argv[3]
    DATA_PORT       = sys.argv[4]

# Length of 6 means filename was included
elif len(sys.argv) == 6:
    HOST            = sys.argv[1]
    CONTROL_PORT    = sys.argv[2]
    COMMAND         = sys.argv[3]
    FILENAME        = sys.argv[4]
    DATA_PORT       = sys.argv[5]

# Improper usage
else:
    print "Usage: python " + sys.argv[0] + " <server host> <server port> <command: -l | -g filename> <data port>"
    exit(1)

# Connect to control connection
control = initiateContact(HOST, CONTROL_PORT)

# Send request to server
makeRequest()

# Response indicates on which connection to receive (control/data)
response = control.recv(1024)

# Receive on data connection
if response == "DATA":
    # Connect to data connection
    data = initiateContact(HOST, DATA_PORT)
    
    # list command
    if COMMAND == "-l":
        listing = data.recv(1024)
        print "Receiving directory structure from " + HOST + ":" + DATA_PORT
        print listing

    # get command
    if COMMAND == "-g":
        receiveFile()

# Close control connection
control.close()
exit(0)