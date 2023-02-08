from os import listdir


def send_file(socket, filename, recv_check):
    # Use recv_check to ensure validity of exchange, raise error otherwise.
    if recv_check == "Success":
        # Open the file in  binary mode.
        with open(filename, "rb") as file:
            # Read the contents of the file and send to client/server until no more data to send.
            while True:
                bytes_ = file.read(1024)
                if not bytes_:
                    break
                try:
                    bytes_sent = socket.sendall(bytes_)
                except OSError as e:
                    raise Exception(e)
    else:
        raise Exception(recv_check)
    return bytes_sent


def recv_file(socket, filename, recv_check):
    bytes_read = 0

    # Use recv_check to ensure validity of exchange, raise error otherwise.
    if recv_check == "Success":
        # Open file in binary mode.
        with open(filename, "wb") as file:
            # Loop until all data sent from client/server has been received and written into new file.
            while True:
                bytes_ = socket.recv(1024)
                if not bytes_:
                    break

                file.write(bytes_)
                bytes_read += len(bytes_)
    else:
        raise Exception(recv_check)
    return bytes_read


def send_listing(socket):
    sep_ = "<:::>"
    directory = listdir('./server')

    # Loop through directory and send names to client.
    # Use a separator to split string later.
    for i in directory:
        socket.send(f"{i}{sep_}".encode())
    return


def recv_listing(socket):
    total = ""

    # Loop until all bytes from server received.
    # Return the string of names split via the separator included.
    while True:
        bytes_ = socket.recv(1024)
        if not bytes_:
            break
        total = total+bytes_.decode()
    return total.split("<:::>")

