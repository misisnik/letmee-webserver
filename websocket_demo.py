import time
import machine
from ws_connection import ClientClosedError
from ws_server import WebSocketServer, WebSocketClient

class WebsocketClient(WebSocketClient):
    def __init__(self, conn):
        super().__init__(conn)

    def process(self, *args, **kwargs):
        # first is something from attiny ?
        try:
            msg = self.connection.read()
            if msg:
                # something from websoket
                msg = msg.decode("utf-8")
                items = msg.split(" ")
                cmd = items[0]
            # check if something is for change
            if uart_flag:
                # yes something needs to be send by webcocket for client side
                self.connection.write('tralalallal')
        except ClientClosedError:
            self.connection.close()


class WebsocketServer(WebSocketServer):
    def __init__(self):
        super().__init__('index.html', 1) #allow only 1 connection on it

    def _make_client(self, conn):
        return WebsocketClient(conn)

class LetMee(object):
    def __init__(self):
        # basic definitons of tiny variables with target info
        self.varInit()
        # initialize of attiny UART communication
        self.attiny = self.attinyInit()
        # initialize the websocker server for it
        self.websocketInit()
        # and run main loop
        self.run()

    def varInit(self):
        self.uartFlag = True # is something new from UART??
        self.newData = {} # new data for uart send
        # database with all data of target
        # t = number of targets
        # c = array of shooted part of each target
        self.target = { 't': 1
                      , 'c': {1:[]} }

    def attinyInit(self):
        pass

    def websockerInit(self):
        self.server = WebsocketServer()
        self.server.start()

    def checkUart(self):
        # todo UART read something if exist and set timeout on it because i want !
        uart = True
        # if something come put into variable and set incomming flag to 1
        if uart:
            self.uartFlag = True
            # self.new_data = {'1':'nejaka nova data'}

    def run(self):
        try:
            while 1:
                self.server.procecss_all( uart_flag = self.uartFlag
                                        , new_data  = self.new_data )
                # set uart event flah to 0 and new_data erase
                self.uartFlag = False
                self.new_data = {}
                # something on UART??
                self.checkUart()
                time.sleep(1)
        except KeyboardInterrupt:
            self.server.stop()
