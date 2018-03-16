import socket
import sys
import threading
import struct
import pickle

serveraddr = (socket.gethostname(), 5000)


class ServerChat:
    def __init__(self):
        self.__socket = socket.socket()
        self.__socket.bind(serveraddr)
        self.__clients = {}

    def run(self):
        self.__socket.listen()
        while True:
            (clientsocket, address) = self.__socket.accept()
            print(clientsocket, address)
            clientrcv = self._receive(clientsocket)
            try:
                if clientrcv == 'clients':
                    self._handle(clientsocket)
                elif clientrcv == 'port':
                    clientsocket.send(str(address[1]).encode())
                elif clientrcv == 'disconnect':
                    for i, j in self.__clients.items():
                        if j[0] == address[0]:
                            del self.__clients[i]
                else:
                    self.__clients[clientrcv] = address
                    clientsocket.send(("{} {} {}".format(clientrcv, address[0], address[1])).encode())
                clientsocket.close()
            except OSError:
                print('Reception Error !')

    def _handle(self, client):
        clientrcv = ""
        for i, j in self.__clients.items():
            clientrcv += ("{} {} {}\n".format(i, j[0], j[1]))
        print(clientrcv)
        client.send(clientrcv.encode())
    
    def _receive(self, clientsocket):
        size = struct.unpack('I', clientsocket.recv(4))[0]
        data = pickle.loads(clientsocket.recv(size)).decode()

        return data


class Chat:
    def __init__(self):
        self.__pseudo = input("Enter your pseudo here :\n")
        self.__port = None
        self.__ip = None
        self.__listofclients = {}

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/quit': self._quit,
            '/join': self._join,
            '/send': self._send,
            '/chat': self._chat,
            '/clients': self._client_on_serv,
            '/connect': self._name
        }
        for i in handlers.keys():
            print(i)
        print("Enter command !")
        self.__running = True
        self.__address = None

        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ') + 1:].rstrip()
            # Call the command handler
            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Erreur lors de l'exécution de la commande.")
            else:
                print('Command inconnue:', command)

    def _chat(self):
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((socket.gethostname(), int(self.__port)))
        self.__s = s
        print('Écoute sur {}:{}'.format(socket.gethostname(), int(self.__port)))
        threading.Thread(target=self._receive).start()

    def _exit(self):
        self._connection("disconnect")
        self.__running = False
        self.__address = None
        self.__s.close()

    def _quit(self):
        try:
            print("Disconnected from " + str(self.__address[0]))
            self.__address = None
        except TypeError:
            print("No connection")

    def _join(self, param):
        tokens = self.__listofclients[param]
        try:
            self.__address = (param, (tokens['ip'], int(tokens['port'])))
            print('Connecté à {}:{}'.format(*self.__address))
        except OSError:
            print("Erreur lors de la tentative de connection")

    def _send(self, param):
        if self.__address is not None:
            try:
                print("To " + "[" + self.__address[0] + "]" + ": "+param)
                message = (self.__pseudo + " " + param).encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__address[1])
                    totalsent += sent
            except OSError:
                print('Erreur lors de la réception du message.')

    def _receive(self):
        if self.__s is not None:
            while self.__running:
                try:
                    data, address = self.__s.recvfrom(1024)
                    msg = data.decode()
                    pseudo = msg.split(" ")[0]
                    message = msg.split(" ")[1]
                    print(" [" + pseudo + "]" + ": " + message)
                    if pseudo not in self.__listofclients:
                        print("Type \"/join " + pseudo + "\" to start chatting with " + pseudo)
                        self._clients()

                except socket.timeout:
                    pass
                except OSError:
                    return

    def _client_on_serv(self):
        self._clients()
        print("Clients on ChatServer :")
        for i in self.__listofclients.keys():
            print(i)

    def _clients(self):
        clients = self._connection("clients")
        List_of_clients = {}
        for i in clients.split("\n")[:-1]:
            data = i.split(" ")
            name = data[0]
            ip = data[1]
            port = data[2]
            coords = {"ip":None,"port":None}
            coords["ip"] = ip
            coords["port"] = port
            List_of_clients[name] = coords
        self.__listofclients = List_of_clients
        return self._listofclients

    def _name(self):
        pseudo_port = (self._connection(self.__pseudo)).split(" ")
        self.__pseudo = pseudo_port[0]
        self.__ip = pseudo_port[1]
        self.__port = pseudo_port[2]
        self.__listofclients[pseudo_port[0]] = {"ip": self.__ip, "port": self.__port}
        self._chat()
        print(pseudo_port)

    def _connection(self, message):
        self.__t = socket.socket()
        self.__t.connect(serveraddr)
        try:
            totalsent = 0
            msg = pickle.dumps(message.encode())
            self.__t.send(struct.pack('I', len(msg)))
            while totalsent < len(msg):
                sent = self.__t.send(msg[totalsent:])
                totalsent += sent
            data = self.__t.recv(1024).decode()

            return data

        except OSError:
            print("Error with the server connection.")


if __name__ == '__main__':
    
    if len(sys.argv) == 3:
        Chat(sys.argv[1], int(sys.argv[2])).run()
        ServerChat(sys.argv[1], int(sys.argv[2])).run()
    else:
        Chat().run()
        ServerChat().run()
