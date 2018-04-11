# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

import socket
import select
import threading
import sys
from model import *

################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.model = model;
        self.port = port;
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM);
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
        self.soc.bind(('', port));
        self.soc.listen(1);
        self.socks = {};
        self.socks[self.soc] = "SERVER";

    def sendCharacters(self, s):
        for char in self.socks:
            s.send(self.socks[char].encode());

    def sendMap(self, s):
        if len(sys.argv) == 3:
            s.sendall(str(sys.argv[2]).encode());
        else:
            s.sendall(DEFAULT_MAP.encode());
        self.socks[s] = s.recv(64);
        self.model.add_character(self.socks[s]);
        self.sendCharacters(s);
        # envoyer fruits, joueurs, ticks bombes

    def disconnectClient(self, s):
        self.model.quit(self.socks[s]);
        del self.socks[s];
        s.close();

    # time event

    def tick(self, dt):
        sel = select.select(self.socks, [], [], 0);
        if sel[0]:
            for s in sel[0]:
                if s is self.soc:
                    self.sendMap(s.accept()[0]);
                else:
                    msg = s.recv(4096);
                    if len(msg <= 0):
                        self.disconnectClient(s);
        return True

################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, model, host, port, nickname):
        self.model = model;
        self.host = host;
        self.port = port;
        self.nickname = nickname;
        self.soc = None;
        try:
            request = socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM);
        except:
            print("Error : can't connect to server.\n");
            sys.exit(1);
        for res in request:
            try:
                self.soc = socket.socket(res[0], res[1]);
            except:
                self.soc = None;
                continue;
            try:
                self.soc.connect(res[4]);
            except:
                self.soc.close();
                self.soc = None;
                continue;
            print("Connected.\n");
            break;
        if self.soc is None:
            print("Error : can't open connection.\n");
            sys.exit(1);
        self.model.load_map(self.soc.recv(64).decode());
        self.soc.send(nickname.encode());
        self.receiveCharacters(self.soc);

    def receiveBombs(self, s):
        

    def receiveFruits(self, s):


    def receiveCharacters(self, s):
        msg = s.recv(256);
        if len(msg) <= 0:
            return;
        else:


    # keyboard events

    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False

    def keyboard_move_character(self, direction):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        # ...
        return True

    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        # ...
        return True

    # time event

    def tick(self, dt):
        # ...
        return True
