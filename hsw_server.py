from flask import Flask
from flask_socketio import SocketIO
import threading

app = Flask(__name__)
sio_server = SocketIO(app)

@sio_server.on("request")
def request_passer(data):
    sio_server.emit("request", data)

@sio_server.on("response")
def response_passer(token):
    sio_server.emit("response", token)

@app.route("/")
def index_view():
    with open("hcaptcha-js/hsw.js") as fp:
        code = fp.read()

    return f"""
    <html>
    <head></head>
    <body>
        <img src="https://bigrat.monster/media/bigrat.png" alt="An image of a big rat sitting on a man's leg.">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>{code}</script>
        <script type="text/javascript" charset="utf-8">
            var socket = io()
            socket.on('request', async function(data) {{
                console.log(data)
                let token = await hsw(data)
                socket.emit('response', token)
            }})
        </script>
    </body>
    </html>
    """

sio_server.run(app, port=9932)