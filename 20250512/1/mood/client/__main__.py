"""Client side of MOOD"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from client import *


def main():
    """Parses arguments and passes them to start_client, also creates a thread for receiving messages"""
    parser = ArgumentParser()
    parser.add_argument("login", action="store")
    parser.add_argument("port", action="store",
                        default=1337, type=int, nargs='?')
    parser.add_argument("host", action="store",
                        default="localhost", nargs='?')
    parser.add_argument("--file",
                        default="")
    args = parser.parse_args()
    print(args.login)
    print("<<< Welcome to Python-MUD 0.1 >>>")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        s.send(args.login.encode())
        recv = threading.Thread(target=receiver, args=(s, ))
        recv.start()
        if args.file:
            with open(args.file) as f:
                cmd_line(sock=s, stdin=f).cmdloop()
        else:
            cmd_line(sock=s).cmdloop()
        s.shutdown(socket.SHUT_RDWR)
    recv.join()
    sys.exit(0)


if __name__ == "__main__":
    main()
