import multiprocessing
import socketio


lock = multiprocessing.Lock()
event = multiprocessing.Event()
proof = None

def on_response(token):
    global proof
    proof = token
    event.set()

def get_proof(data):
    sio = socketio.Client()
    sio.connect("http://localhost:9932")
    sio.on("response", handler=on_response)

    with lock:
        sio.emit("request", data)
        event.wait()
        event.clear()
        sio.disconnect()
        return proof
