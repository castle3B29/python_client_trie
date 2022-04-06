

from argparse import ArgumentParser
from UserInterface import UserInterface
from DeSerializer import DeSerializer
from Callback import Callback
from Callback import validate_user_socket
from Signalhandler import init_keyboard_catch
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024
def main():
    client_api = UserInterface()
    serializer = DeSerializer()
    parser = ArgumentParser()
    parser.add_argument('--ip', required=True)
    parser.add_argument('--port', required=True)
    args = parser.parse_args()
    address = args.ip
    try:
        port = int(args.port)
        user_check = validate_user_socket(address, port)
    except ValueError:
        print("Invalid port")
        user_check = False

    if user_check:
        client_callback = Callback(BUFFER_SIZE, address, port)
        client_callback.connect_tcp()
        init_keyboard_catch()
        result_startup = client_api.startup_check(client_callback, serializer)
        if result_startup:
            client_api.api(client_callback, serializer)
        client_callback.socket.close()

    else:
        print("WE FAILED TO START THE CLIENT")


if __name__ == '__main__':
    main()
