# File Transfer

Simple 2-connection client-server file transfer system using C++ and Python

## Usage
1. Place ftserver.cpp and text files in one folder
2. Place ftclient.py in another folder

3. Compile ftserver.cpp with:
`g++ -std=c++11 ftserver.cpp -o ftserver`

4. Running ftserver:
`ftserver <port number>`

5. Running ftclient:
`python ftclient.py <server host> <server port> <-l | -g filename> <data port>`

   Requesting the directory structure:  `python ftclient.py flip1 50123 -l 40321`

   Requesting a file:  `python ftclient.py flip1 50123 -g shortfile.txt 40321`

6. Terminate ftserver with Ctrl+C
