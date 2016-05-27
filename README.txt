Nancy Chan
CS 372
Program 2
Description: A simple 2-connection client-server file transfer system

Instructions:
1. Place ftserver.cpp in one folder.
2. Place ftclient.py in another folder.

3. Compile ftserver.cpp with:
g++ -std=c++11 ftserver.cpp -o ftserver

4. Running ftserver:
Usage: ftserver <port number>
Example: ftserver 50123

5. Running ftclient:
Usage: python ftclient.py <server host> <server port> <-l | -g filename> <data port>
The examples assume that ftserver is running on "flip1". Substitute "flip1" with the appropriate host as necessary.

Requesting the directory structure:
python ftclient.py flip1 50123 -l 40321

Requesting a file:
python ftclient.py flip1 50123 -g shortfile.txt 40321

6. Terminate ftserver with Ctrl+C




