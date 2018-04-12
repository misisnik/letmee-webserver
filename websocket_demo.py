import time
# import machine
import ujson
from ws_connection import ClientClosedError
from ws_server import WebSocketServer, WebSocketClient

_TARGETS = 1
_INIT_FLAG = 0
_MODE = 0
_UART_FLAG = True
_NEW_DATA = {'t':0, 'e': -1, 'p': 0} # t = target no, e = LED no, p = points

class Client(WebSocketClient):
    def __init__(self, conn):
        super().__init__(conn)

    def process(self):
        # first is something from attiny ?
        try:
            msg = self.connection.read()
            if msg:
                # something from websoket
                msg = msg.decode("utf-8")
                # json decode
                try:
                    msg = ujson.loads(msg)
                    if msg['i'] == 1:
                        global _INIT_FLAG
                        _INIT_FLAG = 1
                        # needs to send init data
                        d = {'i':1, 'd': {'m': _MODE, 't': _TARGETS}}
                        self.websocketWrite(d)
                    else:
                        # something else so parse
                        pass
                except:
                    # someting happend
                    print('je to napicu neco se stalo')
            # check if something is for change
            if _UART_FLAG:
                # yes something needs to be send by webcocket for client side
                d = {'i':2, 'd': _NEW_DATA}
                self.websocketWrite(d)

        except ClientClosedError as e:
            print('socket error')
            print(e)
            self.connection.close()

    def websocketWrite(self, data):
        self.connection.write(ujson.dumps(data))


class Server(WebSocketServer):
    def __init__(self):
        super().__init__('index.html.gz', 1) #allow only 1 connection on it

    def _make_client(self, conn):
        return Client(conn)

class Letmee(object):
    def __init__(self):
        # initialize of attiny UART communication
        self.attiny = self.attinyInit()

    def attinyInit(self):
        pass

    def checkUart(self):
        # todo UART read something if exist and set timeout on it because i want !
        # _NEW_DATA = {'t':0, 'e': 0, 'p': 0}
        return {'t':0, 'e': _NEW_DATA['e'] + 1, 'p': _NEW_DATA['p'] + 1}

print('start')
server = Server()
letmee = Letmee()
server.start()
try:
    while True:
        server.process_all()
        server.process_all()
        # set uart event flah to 0 and new_data erase
        _UART_FLAG = False
        # _NEW_DATA = {}
        # something on UART??
        if _INIT_FLAG:
            _NEW_DATA = letmee.checkUart()
            _UART_FLAG = True
        time.sleep(1)
except Exception as e:
    print('foooooo')
    print(e)
except KeyboardInterrupt:
    pass
server.stop()
