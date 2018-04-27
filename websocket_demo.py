import time
from machine import UART
import network
import ujson
import ubinascii
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
        self.config = self.loadConfig()
        self.setNetwork()
        self.attiny = self.attinyInit()

    def loadConfig(self):
        """
            Load json data from config file with all settings
        """
        with open('config', 'r') as f:
            config = f.readline()
        return ujson.loads(config)

    def saveConfig(self, config = None):
        """
            Save config file from self.config if is not defined
        """
        # change config file
        with open('config', 'w') as f:
            if config == None:
                config = self.config
            f.write(ujson.dumps(config))
        self.config = config

    def getMac(self):
        """
            Return mac address of the tag
        """
        return ubinascii.hexlify(network.WLAN().config('mac'),':').decode()

    def setNetwork(self):
        name = '{}-{}'.format(self.config['name'], self.getMac()[-4:])
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(True)
        if ap_if.config('essid') != name:
            # new wifi config will send only if new wifi name occure
            ap_if.config( essid    = name
                        , password = self.config['pass'] )

    def attinyInit(self):
        # define UART
        self.uart = UART(0, 9600)
        self.uart.init(9600, bits=8, parity=None, stop=2)

    def checkUart(self):
        # todo UART read something if exist and set timeout on it because i want !
        # _NEW_DATA = {'t':0, 'e': 0, 'p': 0}
        # return {'t':0, 'e': _NEW_DATA['e'] + 1, 'p': _NEW_DATA['p'] + 1}

        # readline with timeout
        try:
            line = self.uart.readline()
            line = line.decode('utf-8')[:-1]
            print(line)
            return ujson.loads(line)
        except Exception as e:
            print(e)
            return False

letmee = Letmee()
server = Server()
while 1:
    server.start()
    print('server_started')
    try:
        while True:
            server.process_all()
            # set uart event flag to 0 and new_data erase
            _UART_FLAG = False
            # something on UART??
            if _INIT_FLAG:
                uart_data = letmee.checkUart()
                if uart_data:
                    _NEW_DATA = uart_data
                    _UART_FLAG = True
            time.sleep(1)
    except Exception as e:
        print('foooooo')
        print(e)
    except KeyboardInterrupt:
        pass
    server.stop()
    try:
        # time to kill process, else server will start again
        print('Websocket server kill = ctrl + c')
        time.sleep(1)
    except KeyboardInterrupt:
        break
