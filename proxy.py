from socket import *
import sys
if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IPAddress Of Proxy Server')
    sys.exit(2)
# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
# Fill in start.
# Bind to the provided server IP and port 8888, then listen for connections
tcpSerSock.bind((sys.argv[1], 8888))
tcpSerSock.listen(5)
# Fill in end.
while 1:
    # Strat receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    # Receive the client's request message (decode to str)
    message = tcpCliSock.recv(1024).decode()
    print(message)
    # Extract the filename from the given message
    print(message.split()[1])
    filename = message.split()[1].partition("/")[2]
    print(filename)
    fileExist = "false"
    filetouse = "/" + filename
    print(filetouse)
    try:
     # Check wether the file exist in the cache
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()
        fileExist = "true"
        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send("HTTP/1.0 200 OK\r\n")
        tcpCliSock.send("Content-Type:text/html\r\n")
        # Send the cached file content to the client
        for line in outputdata:
            try:
                tcpCliSock.send(line.encode())
            except:
                # fall back to sending raw line if already bytes
                tcpCliSock.send(line)
        print('Read from cache')
    # Error handling for file not found in cache
    except IOError:
        if fileExist == "false":
            # Create a socket on the proxyserver
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace("www.","",1)
            print(hostn)
            try:
                # Connect to the socket to port 80
                c.connect((hostn, 80))
                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                # Send the GET request to the remote server
                request_line = "GET http://" + filename + " HTTP/1.0\r\n\r\n"
                c.sendall(request_line.encode())
                # Read the response into a buffer (streaming)
                response_buffer = b""
                # We'll read in chunks and stream to the client and cache
                data = c.recv(4096)
                while data:
                    response_buffer += data
                    data = c.recv(4096)
                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socketand the corresponding file in the cache
                tmpFile = open("./" + filename,"wb")
                # write the collected response to cache and send to client
                try:
                    tmpFile.write(response_buffer)
                    tcpCliSock.send(response_buffer)
                except Exception:
                    # if something goes wrong while sending/writing, ensure we don't crash
                    pass
                finally:
                    tmpFile.close()
            except:
                print("Illegal request")
        else:
            # HTTP response message for file not found
            tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode())
            tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
    # Close the client and the server sockets
    tcpCliSock.close()
    # Close any connection to the remote server if present
    try:
        c.close()
    except:
        pass