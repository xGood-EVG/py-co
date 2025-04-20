import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server import *

if __name__ == "__main__":
    cm = Communicator()
    fld = Field(FIELDX, FIELDY, cm)
    port = 1337 if len(sys.argv) < 2 else int(sys.argv[1])
    host = "localhost" if len(sys.argv) < 3 else sys.argv[2]
    movement = threading.Thread(target=random_move)
    movement.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            client = threading.Thread(target=handler, args=(conn, addr, cm, fld))
            client.start()