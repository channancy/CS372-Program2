"""
Nancy Chan
CS 372

Program 2
Description: A simple 2-connection client-server file transfer system

Filename: ftclient.py
Usage: python ftclient.py <server host> <server port> <-l | -g filename> <data port>
Description: File Transfer Client
- Starts on a host and validates command line parameters
- Establishes a TCP control connection (P) with the server
- Sends commands and receives control messages on P
- Establishes a TCP data connection (Q) with the server
- Receives either a directory listing or contents of a text file on Q
- Saves the contents to a file, handling duplicate filenames if necessary
- Closes P

Sources cited:
https://docs.python.org/2/library/socket.html
http://stackoverflow.com/questions/82831/how-to-check-whether-a-file-exists-using-python
"""

import socket
import sys
import os.path

def validateParameters(target_command):
    """
    Validate command line argument values
    """
    valid = True

    # Check if integer
    if CONTROL_PORT.isdigit():
        # Check against range of ports
        if int(CONTROL_PORT) < 1024 or int(CONTROL_PORT) > 65535:
            valid = False
            print "Control port must be an integer between 1024 and 65535"
    # Not integer is invalid
    else:
        valid = False
        print "Control port must be an integer between 1024 and 65535"

    # Check if valid command
    if COMMAND != target_command:
        valid = False

    # Check if integer
    if DATA_PORT.isdigit():
        # Check against range of ports
        if int(DATA_PORT) < 1024 or int(DATA_PORT) > 65535:
            valid = False
            print "Data port must be an integer between 1024 and 65535"
    # Not integer is invalid
    else:
        valid = False
        print "Data port must be an integer between 1024 and 65535"

    # Check if failed any requirements
    if valid == False:
        print "Usage: python " + sys.argv[0] + " <server host> <server port> <command: -l | -g filename> <data port>"
        exit(1)

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
    response = control.recv(1024)

    # If response is an integer, then response is file size
    if response.isdigit():
        filesize = int(response)
    # Else response is error message
    else:
        print HOST + ":" + CONTROL_PORT + " says " + response
        exit(1)

    # Initialize variables to be concatenated/incremented
    filecontents = ""
    bytes_sent_total = 0

    print 'Receiving "' + FILENAME + '" from ' + HOST + ":" + DATA_PORT

    # Empty the file (write mode to overwrite)
    open(FILENAME, 'w').close()

    # Open the file (append mode to append as more contents received)
    fo = open(FILENAME, 'a')

    # Receive file contents in increments of 1000 until reach file size
    while bytes_sent_total < filesize:
        filecontents = data.recv(1000)
        # Write file contents to file
        fo.write(filecontents)
        # Update total
        bytes_sent_total += 1000

    # Close the file
    fo.close()

    print "File transfer complete"

#----------------------------------------
# Main Program
#----------------------------------------

# Validate command line arguments
# Length of 5 means filename not included
if len(sys.argv) == 5:
    HOST            = sys.argv[1]
    CONTROL_PORT    = sys.argv[2]
    COMMAND         = sys.argv[3]
    DATA_PORT       = sys.argv[4]

    # Should be list command
    validateParameters("-l")

# Length of 6 means filename was included
elif len(sys.argv) == 6:
    HOST            = sys.argv[1]
    CONTROL_PORT    = sys.argv[2]
    COMMAND         = sys.argv[3]
    FILENAME        = sys.argv[4]
    DATA_PORT       = sys.argv[5]

    # Should be get command
    validateParameters("-g")

    # Check extension of file
    if not FILENAME.endswith(".txt"):
        print "Requested file must be a text file"
        exit(1)

    # Handle duplicate file
    if os.path.isfile(FILENAME):
        print '"' + FILENAME + '" already exists in the directory. Overwrite the file? (y/n)'
        overwrite = raw_input()
        # Case insensitive comparison
        if overwrite.lower() == "y":
            print '"' + FILENAME + '" will be requested and overwritten'
        else:
            print 'Request for "' + FILENAME + '" has been cancelled'
            exit(0)

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