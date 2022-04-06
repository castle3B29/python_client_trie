import socket
from struct import unpack

SOCKET_TIMEOUT = 15
USER_TIMEOUT = 5
ZERO_BYTES = 0

IPV4_PARTS = 4
IPV4_HIGHEST_VAL = 255

PORT_MIN = 1024
PORT_MAX = 65535

def validate_ip_address(user_address):
    octets = user_address.split(".")
    if len(octets) != IPV4_PARTS:
        print("Provided IP address is not valid")
        return False
    for octet in octets:
        if not isinstance(int(octet), int):
            print("Provided IP addrses is not valid")
            return False
        if int(octet) < 0 or int(octet) > IPV4_HIGHEST_VAL:
            print("Provided IP address is not valid")
            return False
    print("Provided IP address is valid")
    return True

def validate_port(user_port):
    if PORT_MIN < user_port < PORT_MAX:
        print("port is valid")
        return True
    else:
        print("Bad port")
        return False

def validate_user_socket(user_address, user_port):
    result = validate_ip_address(user_address)
    if not result:
        print("Fail on ip")
        return False
    result = validate_port(user_port)
    if not result:
        print("Fail on port")
        return False
    return result

class Callback:
    def __init__(self, buffer_size, host, port):
        self.buffer_size = buffer_size
        self.host, self.port = host, port 
        self.socket = None
        self.end = False
        self.trans_id = 0
    def connect_tcp(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(SOCKET_TIMEOUT)
        except ConnectionRefusedError:
            self.socket.close()
            print("Failed to connect to server")
        

    def send_req(self, bytes_msg, trans_id):
        response = self.check_packet(bytes_msg)
        if not response:
            return False

        try:
            print("Transaction {}", trans_id)
            print("Waiting on server.....")    
            self.socket.send(bytes_msg)
            return True
        except:
            print("you have been logged out")
            return False
    
    def receive_req(self):
        data = self.socket.recv(1024)
        if not data:
            print("We received a interruption")
        else:
            print(data)
            print("We got some data back")
        return data

    def send_resp(self, bytes_msg):
        try:
            print("Waiting on server.....")    
            self.send(bytes_msg)
        except:
            print("We received an error....recommend connectivity check as next action")

    def verify_connection(self, trans_id, bytes_msg):
        try:
            self.socket.send(bytes_msg)
            server_response = self.socket.recv(1024)
            if not server_response:
                print("Server unreachable")
                return False
            else:
                if ( trans_id == unpack('!L', server_response[3:7])[0]):
                    return True
                else:
                    return False
        except:
            print("You have been logged out")
            return False

    def check_packet(self, bytes_msg):
        if ( ZERO_BYTES == len (bytes_msg)):
            return False
        else:
            return True
    
