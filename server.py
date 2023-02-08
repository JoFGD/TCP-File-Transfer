import socket
import sys
from os import path
from module import recv_file, send_file, send_listing

srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

""" 
 Enclose the following two lines in a try-except block to catch
 exceptions.
"""
try:
    """
     Register the socket with the OS kernel so that messages sent
     to the user-defined port number are delivered to this program.
     Using "0.0.0.0" as the IP address so as to bind to all available
     network interfaces. 
    """
    srv_sock.bind(("0.0.0.0", int(sys.argv[1])))

    """
     Create a queue where new connection requests will be added by
     the OS kernel. 
    """
    srv_sock.listen(5)
except Exception as e:
    # Print the exception message
    print(e)
    # Exit with a non-zero value, to indicate an error condition
    exit(1)

# Loop forever (or at least for as long as no fatal errors occur)
while True:
    """
     Surround the following code in a try-except block to account for errors.
    """
    try:
        # Initialise variables.
        code = "no_code"
        filename = "no_filename"
        """
         Dequeue a connection request from the queue created by listen() earlier.
         If no such request is in the queue yet, this will block until one comes
         in. Returns a new socket to use to communicate with the connected client
         plus the client-side socket's address (IP and port number).
        """
        cli_sock, cli_addr = srv_sock.accept()

        # Receive a message confirming the arguments have been input correctly.
        message = cli_sock.recv(1024).decode()

        if message == "Success":
            # Return message to continue client, and stop messages from merging.
            cli_sock.send("continue".encode())

            # Receive arguments, including filename and code.
            recv = cli_sock.recv(1024).decode()
            recv_args = recv.split("<:::>")

            # Check number of  arguments, over 2 suggests an error has been raised.
            if len(recv_args) > 2:
                code, filename = recv_args[0], recv_args[1]
                raise Exception(recv_args[2])
            else:
                code, filename = recv_args[0], recv_args[1]

            if code == "put":
                # Check file exists in directory and throw error otherwise.
                if path.exists("server/"+filename):
                    cli_sock.send("[ERROR] File already exists in directory.".encode())
                    raise Exception("[ERROR] File already exists in directory.")

                # Send confirmation to client that no error has occurred, and receive confirmation back.
                cli_sock.send("Success".encode())
                recv_check = cli_sock.recv(1024).decode()

                # Function for receiving the file to be put on server.
                bytes_ = recv_file(cli_sock, "server/"+filename, recv_check)

            elif code == "get":
                # Check file doesn't exist in server already and throw error otherwise.
                if not path.exists("server/"+filename):
                    cli_sock.send("[ERROR] File being sent does not exist in directory.".encode())
                    raise Exception("[ERROR] File being sent does not exist in directory.")

                # Send confirmation to client that no error has occurred, and receive confirmation back.
                cli_sock.send("Success".encode())
                recv_check = cli_sock.recv(1024).decode()

                # Function for sending the file to client.
                bytes_ = send_file(cli_sock, "server/"+filename, recv_check)

            elif code == "list":
                # Function for sending file names to be listed on client.
                bytes_ = send_listing(cli_sock)

            print(f"IP:{cli_addr[0]} Port:{cli_addr[1]} Code:{code} File_name:{filename} Success")
        else:
            raise Exception(message)

    except Exception as e:
        print(f"IP:{cli_addr[0]} Port:{cli_addr[1]} Code:{code} File_name:{filename} Failure:{e}")

    finally:
        """
         If an error occurs or the client closes the connection, call close() on the
         connected socket to release the resources allocated to it by the OS.
        """
        cli_sock.close()

# Close the server socket as well to release its resources back to the OS
srv_sock.close()

# Exit with a zero value, to indicate success
exit(0)



