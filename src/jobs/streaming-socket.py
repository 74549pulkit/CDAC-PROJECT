import json  # Import the JSON module for working with JSON data
import socket  # Import the socket module for establishing socket connections
import time  # Import the time module for adding delays
import pandas as pd  # Import the pandas library for working with DataFrames

def handle_date(obj):
    """Function to handle conversion of pandas Timestamp objects to a string format."""
    if isinstance(obj, pd.Timestamp):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def send_data_over_socket(file_path, host='spark-master', port=9998, chunk_size=3):
    """
        Function to send data over a socket connection in chunks.

        Args:
            file_path (str): The path to the file containing the data to be sent.
            host (str): The hostname or IP address to bind the socket to.
            port (int): The port number to bind the socket to.
            chunk_size (int): The size of each chunk of data to be sent.

    """
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    """ socket.AF_INET: This parameter specifies the address family of the socket. 
                       In this case, it indicates that the socket will use IPv4 addresses.

        socket.SOCK_STREAM: This parameter specifies the type of the socket. 
                            SOCK_STREAM indicates a stream socket, which provides a sequenced, reliable, two-way, connection-based byte stream.
    """
    # Bind the socket to the host and port
    s.bind((host, port))
    # Listen for incoming connections
    s.listen(1)
    print(f"Listening for connections on {host}:{port}")

    last_sent_index = 0  # Initialize the index of the last sent record
    while True:
        # Accept a connection from a client
        conn, addr = s.accept()
        print(f"Connection from {addr}")
        try:
            with open(file_path, 'r') as file:
                # Skip the lines that were already sent
                for _ in range(last_sent_index):
                    next(file)

                records = []  # Initialize a list to store records
                for line in file:
                    records.append(json.loads(line))  # Parse JSON data and append to records list
                    if len(records) == chunk_size:  # Check if the chunk size is reached
                        chunk = pd.DataFrame(records)  # Create a DataFrame from the records
                        
                        chunk['row_no'] = chunk.index + 1  # Resetting the index to create a new column with row numbers  ******

                        print(chunk)  # Print the chunk (optional)
                        for record in chunk.to_dict(orient='records'):
                            serialize_data = json.dumps(record, default=handle_date).encode('utf-8')  # Serialize the data to JSON format
                            conn.send(serialize_data + b'\n')  # Send the serialized data over the socket
                            time.sleep(10)  # Add a delay (optional)
                            last_sent_index += 1  # Update the index of the last sent record

                        records = []  # Clear the records list for the next chunk
        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected.")
        finally:
            conn.close()  # Close the connection
            print("Connection closed")

if __name__ == "__main__":
    send_data_over_socket("datasets/yelp_academic_dataset_review.json")  # Call the function with the specified file path
