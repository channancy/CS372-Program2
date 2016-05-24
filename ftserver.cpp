/*
 * Nancy Chan
 * CS 372
 * 
 * Program 1
 * Description: A simple chat system that works for a pair of users
 * 
 * Filename: chatserve.cpp
 * Usage: chatserve <port number>
 * Description: Chat Server
 * - Gets the user's handle by initial query and displays handle as
 *   a prompt and prepends it to all messages sent.
 * - Waits on a port for a client request.
 * - Alternates sending/receiving messages with a connected client
 *   until the connection is closed by either with '\quit'
 * - The process is repeated until the user terminates it with Ctrl+C
 *
 * Sources cited:
 * Beej's Guide to Network Programming - https://beej.us/guide/bgnet/
 * http://beej.us/guide/bgnet/output/html/multipage/getnameinfoman.html
 * http://www.thegeekstuff.com/2012/06/c-directory/
 * http://stackoverflow.com/questions/4204666/how-to-list-files-in-a-directory-in-a-c-program
 * http://stackoverflow.com/questions/612097/how-can-i-get-the-list-of-files-in-a-directory-using-c-or-c
 * http://stackoverflow.com/questions/20265328/readdir-beginning-with-dots-instead-of-files
 * http://cboard.cprogramming.com/cplusplus-programming/130444-how-do-you-split-string-multiple-words-into-single-words.html
 */

#include <iostream>
#include <string>
#include <sstream>
#include <cstring>
#include <dirent.h> 
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <signal.h>
using namespace std;

// Number of pending connections queue will hold
#define BACKLOG 10
// Size of buffer for recv
#define MAXDATASIZE 5000

// Function prototypes
int startUp(char* portno);
int acceptConnection(int sockfd);
void receiveCommand(int new_fd, char* portno);
string listDirectory();
void sendMessage(string message, int new_fd);
void sigchld_handler(int s);
void *get_in_addr(struct sockaddr *sa);

int main(int argc, char *argv[]) {
    int sockfd, new_fd; // Listen on sockfd, new connection on new_fd
    char* portno;       // Port number

    // Check command line arguments count
    // argv[0] = Program name
    // argv[1] = Port number
    if (argc < 2) {
       fprintf(stderr, "Usage: %s <port number>\n", argv[0]);
       exit(1);
    }

    portno = argv[1];

    // Start connection
    sockfd = startUp(portno);

    // Loop forever
    while (1) {
        // Accept connection
        new_fd = acceptConnection(sockfd);

        // Child process
        if (!fork()) { 
            // Child doesn't need the listener
            close(sockfd);

            // Alternate receiving and sending
            while (1) {
                receiveCommand(new_fd, portno);
            }
        }

        // Parent doesn't need this
        close(new_fd);
    }

    return 0;
}

/* startUp
 * 
 * Start the server with calls to socket(), bind(), and listen()
 */
int startUp(char* portno) {
    // Listen on sockfd
    int sockfd;                         // Socket file descriptor
    struct addrinfo hints;              // Prep the socket address structures
    struct addrinfo *servinfo, *p;      // Point to results
    struct sigaction sa;                // For action to specific signal
    int yes=1;                          // optval for setsockopt()
    int rv;                             // Return value of getaddrinfo()

    memset(&hints, 0, sizeof hints);    // Make sure struct is empty
    hints.ai_family = AF_UNSPEC;        // IP version-agnostic (IPv4 OR IPv6)
    hints.ai_socktype = SOCK_STREAM;    // TCP stream sockets
    hints.ai_flags = AI_PASSIVE;        // Assign my IP address

    // getaddrinfo(IP address, port number, struct addrinfo, results)
    // IP address is NULL because hints.ai_flags = AI_PASSIVE
    // servinfo (results) will point to linked list of 1+ struct addrinfo
    if ((rv = getaddrinfo(NULL, portno, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        exit(1);
    }

    // Walk through servinfo (results) linked list
    for (p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("server: socket");
            continue;
        }

        // Set socket options
        if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes,
                sizeof(int)) == -1) {
            perror("setsockopt");
            exit(1);
        }

        // Bind to the first valid one
        if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            close(sockfd);
            perror("server: bind");
            continue;
        }

        break;
    }

    // Free servinfo structure
    freeaddrinfo(servinfo);

    if (p == NULL)  {
        fprintf(stderr, "server: failed to bind\n");
        exit(1);
    }

    // Wait for incoming connections
    if (listen(sockfd, BACKLOG) == -1) {
        perror("listen");
        exit(1);
    }

    // Reap all dead processes
    sa.sa_handler = sigchld_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if (sigaction(SIGCHLD, &sa, NULL) == -1) {
        perror("sigaction");
        exit(1);
    }

    cout << "Server open on " << portno << endl;

    return sockfd;
}

/* acceptConnection
 * 
 * Accept queued connection and create new socket file descriptor
 */
int acceptConnection(int sockfd) {
    // New connection so original connection is still listening
    // for other new connections
    int new_fd;
    socklen_t sin_size;
    struct sockaddr_storage their_addr; // Connector's address information
    char host[INET6_ADDRSTRLEN];
    char service[20];

    // Pass pointer to info and size of struct for incoming connection
    sin_size = sizeof their_addr;
    new_fd = accept(sockfd, (struct sockaddr *)&their_addr, &sin_size);
    if (new_fd == -1) {
        perror("accept");
        exit(1);
    }

    // Lookup host name for incoming connection
    getnameinfo((struct sockaddr *)&their_addr, sin_size, host, sizeof host, service, sizeof service, 0);
    cout << "Connection from " << host << endl;
    
    // Convert IPv4/IPv6 addresses from binary to text form
    // inet_ntop(their_addr.ss_family,
    //     get_in_addr((struct sockaddr *)&their_addr),
    //     s, sizeof s);
    // printf("Connection from %s\n", s);

    return new_fd;
}

/* receiveCommand
 * 
 * Receive command over stream socket
 */
void receiveCommand(int new_fd, char* portno) {
    int numbytes;
    char buffer[MAXDATASIZE];
    string command, clientport;
    string listing;

    // recv returns number of bytes read into the buffer
    if ((numbytes = recv(new_fd, buffer, MAXDATASIZE - 1, 0)) == -1) {
        perror("recv");
        exit(1);
    }

    // Null-terminate
    buffer[numbytes] = '\0';

    // Display message
    // printf("%s\n", buffer);

    // Convert buffer to stringstream to read from
    istringstream StrStream(buffer);

    // Extract command and clientport
    StrStream >> command;
    StrStream >> clientport;

    // Check command
    // list
    if (command == "-l") {
        cout << "List directory requested on port " << clientport << endl;
        listing = listDirectory();
        cout << "Sending directory contents to " << clientport << endl;
        sendMessage(listing, new_fd);
        close(new_fd);
        exit(0);
    }
}

/* sendMessage
 * 
 * Send message over stream socket
 */
void sendMessage(string message, int new_fd) {
    const char* msg = message.c_str();

    // send returns number of bytes actually sent out
    if (send(new_fd, msg, strlen(msg), 0) == -1) {
        perror("send");
    }
}

string listDirectory() {
    DIR *d;
    struct dirent *dir;
    // Open current directory
    // opendir() returns pointer to directory stream or NULL on error
    d = opendir(".");
    string listing;

    // Not NULL so we have a pointer to the directory stream
    if (d) {
        // Print all files and directories within the directory
        /* readdir() function returns a pointer to a dirent structure representing the
        next directory entry in the directory stream pointed to by dirp. It returns
        NULL on reaching the end of the directory stream or if an error occurred (linux man)*/
        while ((dir = readdir(d)) != NULL) {
            // Do not print current and parent hardlinks (. and ..)
            if (strcmp(dir->d_name, ".") == 0 || strcmp(dir->d_name, "..") == 0) {
            
            }
            else {
                // Print the filename
                // char d_name[256] is the filename variable of the struct
                listing += dir->d_name;
                listing += "\n";
            }
        }

        // Remove the last newline character that was added
        listing.pop_back();
     
        // Close directory
        closedir(d);
    }

    return listing;
}

/* sigchld_handler
 * 
 * Reap zombie processes that appear as the fork()ed child processes exit
 */
void sigchld_handler(int s) {
    // waitpid() might overwrite errno so save and restore it:
    int saved_errno = errno;

    while(waitpid(-1, NULL, WNOHANG) > 0);

    errno = saved_errno;
}

/* *get_in_addr
 *  
 * Get sockaddr, IPv4 or IPv6
 */
void *get_in_addr(struct sockaddr *sa) {
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}
