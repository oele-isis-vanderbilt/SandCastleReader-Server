import os
import time
import subprocess as sp
import threading
import pathlib

from waitress import serve

# Import app
from scrs import app, get_ip_address

# Constants
CWD = pathlib.Path(os.path.abspath(__file__))
LOCAL_IP_ADDRESS = get_ip_address()
GITHUB_FOLDER = CWD.parent.parent
FRONT_END_PATH = GITHUB_FOLDER / 'SandCastleReader'


def run_backend():
    print(f"Running Flask Server at http://{LOCAL_IP_ADDRESS}:5000")
    serve(app, listen="*:5000")


def run_frontend(is_running: threading.Event):
    print(f"Running Vue Server at http://{LOCAL_IP_ADDRESS}:8080")
    p = sp.Popen(['npm', 'run', 'serve'], cwd=str(FRONT_END_PATH))

    while is_running.is_set():
        time.sleep(0.5)

    p.kill()
    p.terminate()


if __name__ == "__main__":

    is_running = threading.Event()
    is_running.set()
    
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.start()

    frontend_thread = threading.Thread(target=run_frontend, args=(is_running,))
    frontend_thread.start()

    try:
        backend_thread.join()
    except KeyboardInterrupt:
        ...

    is_running.clear()
    frontend_thread.join()
