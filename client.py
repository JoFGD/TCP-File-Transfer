import socket
from os import path
import sys
from module import recv_file, send_file, recv_listing

# Create the socket with which we will connect to the server
cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# The server's address is a tuple, comprising the server's IP address or hostname, and port number
srv_addr = (sys.argv[1], int(sys.argv[2]))

filename = "no_filename"
code = "no_code"
received = ""
if len(sys.argv) == 5:
    filename = sys.argv[4]
Sep_ = "<:::>"
bytes_ = 0

# Convert to string, to be used shortly
srv_addr_str = str(srv_addr)

codes = ("put", "get", "list")

""" 
 Enclose the connect() call in a try-except block to catch
 exceptions.
"""
try:

    """
     Connect our socket to the server.  The connect() call will initiate TCP's 3-way
     handshake procedure. On successful return, said procedure will have
     finished successfully, and a TCP connection to the server will have been
     established.
    """
    cli_sock.connect(srv_addr)

except Exception as e:
    # Print the exception message
    print(f"IP:{srv_addr[0]} Port:{srv_addr[1]} Code:{code} File_name:{filename} Failure:{e}")
    # Exit with a non-zero value, to indicate an error condition
    exit(1)

"""
 Surround the following code in a try-except block to account for
 socket errors as well as errors related to user input. 
"""
try:
    # Check input from user was in the correct format, otherwise throw error and notify server.
    if (len(sys.argv) > 5) or (len(sys.argv) < 3):
        cli_sock.send("[ERROR] Incorrect input of arguments.".encode())
        raise Exception("[ERROR] Incorrect input of arguments.")
    else:
        cli_sock.send("Success".encode())

    # Wait for server response.
    cli_sock.recv(1024)

    code = sys.argv[3]

    # Send code and file name to server, raise error if code is incorrect and notify server.
    if code in codes:
        cli_sock.send(f"{code}{Sep_}{filename}".encode())
    else:
        cli_sock.send(f"{code}{Sep_}{filename}{Sep_}[ERROR] Code input incorrect.".encode())
        raise Exception("[ERROR] Code input incorrect.")

    if code == "put":
        # Wait for server to check validity before sending.
        recv_check = cli_sock.recv(1024).decode()

        # Check file exists, otherwise notify server and raise error.
        if not path.exists("client/"+filename):
            cli_sock.send("[ERROR] File being sent does not exist in directory.".encode())
            raise Exception("[ERROR] File being sent does not exist in directory.")

        # Notify server all is correct.
        cli_sock.send("Success".encode())

        # Function for sending file to server.
        bytes_ = send_file(cli_sock, "client/"+filename, recv_check)

    elif code == "get":
        # Wait for server to check validity before sending.
        recv_check = cli_sock.recv(1024).decode()

        # Check file doesn't exist, otherwise notify server and raise error.
        if path.exists("client/"+filename):
            cli_sock.send("[ERROR] File already exists in directory.".encode())
            raise Exception("[ERROR] File already exists in directory.")

        # Notify server all is correct.
        cli_sock.send("Success".encode())

        # Function for receiving file on client.
        bytes_ = recv_file(cli_sock, "client/"+filename, recv_check)

    elif code == "list":
        # Function for receiving list of files in server directory.
        bytes_ = recv_listing(cli_sock)

        # For loop to list names on client.
        print("Listing of server directory:")
        for i in bytes_:
            print(i+"\n")

    print(f"IP:{srv_addr[0]} Port:{srv_addr[1]} Code:{code} File_name:{filename} Success")


except Exception as e:

    print(f"IP:{srv_addr[0]} Port:{srv_addr[1]} Code:{code} File_name:{filename} Failure:{e}")


finally:
    """
     If an error occurs or the server closes the connection, call close() on the
     connected socket to release the resources allocated to it by the OS.
    """
    cli_sock.close()

# Exit with a zero value, to indicate success
exit(0)