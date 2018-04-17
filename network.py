# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

import socket
import select
import threading
import sys
from model import *

################################################################################
#                          AUXILLARY FUNCTION NETWORK                          #
################################################################################

class Command_Network:
    '''
        #Field
        ______

        self.model

        self.isServer

        #Commands
        _________
        """
        Finit les transmissions pour les listes d'objets,
        permet aussi la déconnection (à voire)
        """
        END
        
        """
        Connection d'un joueur avec son nom.
        """
        CON <nicknamePlayer>
        
        """
        Transmission de la map à charger
        """
        MAP <namemap>
        
        """
        Déplace le joueur par son nom
        """
        MOVE <nicknamePlayer> <direction>
        
        """
        Ajoute un joueur
        """
        #player
        A_PLAY <nicknamePlayer> <isplayer> <kind> <pos>
        
        """
        Ajoute une bombe
        """
        A_BOMB <pos> <countdown>
        #model.bombs.append(Bomb(self.map, character.pos))
        
        """
        Ajoute un fruit
        """
        #fruit
        A_FRUIT <kind> <pos X> <pos Y>


    '''

    def __init__(self, model, isServer):
        self.model = model;
        self.isServer = isServer;

    '''
    Encode les commandes pour l'envoi réseau.
    '''
    def enc_command(self, cmd):
        cmd.replace('\\','')

        print ("ENC")
        print (cmd)
        print ()
        
        if cmd.startswith("CON"):
            cmd = cmd.split(" ")
            return str("CON " + cmd[1] + "\\").encode()

        elif cmd.startswith("MAP"):
            cmd =cmd.split(" ")
            return str("MAP " + cmd[1]  +"\\").encode("utf-8")

        elif cmd.startswith("A_PLAY"):
            cmd =cmd.split(" ")
            return str("A_PLAY " + cmd[1] + ' ' + cmd[2] + ' ' + cmd[3] + "\\").encode()

        elif cmd.startswith("D_PLAY"):
            cmd =cmd.split(" ")
            return str("D_PLAY " + cmd[1] + ' ' + cmd[2] + ' ' + cmd[3] ++ ' ' + cmd[4] + "\\").encode()

        elif cmd.startswith("MOVE"):
            cmd = cmd.split(' ')
            return str("MOVE " + cmd[0] + ' ' + cmd[1] + ' ' + cmd[2]  + "\\").encode()

        elif cmd.startswith("T_BOMB"):
            cmd =cmd.split(" ")
            return str("T_BOMB " + cmd[1] + "\\").encode()

        elif cmd.startswith("A_BOMB"):
            cmd =cmd.split(" ")
            return str("A_BOMB " + cmd[1] + ' ' + cmd[2]  + "\\").encode()

        elif cmd.startswith("A_FRUIT"):
            cmd =cmd.split(" ")
            return str("A_FRUIT " + cmd[1] + ' ' + cmd[2]  + ' ' + cmd[3]  +"\\").encode()

        elif cmd.startswith("D_FRUIT"):
            cmd =cmd.split(" ")
            return str("D_FRUIT " + cmd[1] + ' ' + cmd[2] + ' ' + cmd[3]  + "\\").encode()
        
        elif cmd.startswith("END"):
            cmd =cmd.split(" ")
            return str("END " + "\\").encode()

        return None;

    '''
    Decode les commandes.
    Adapte le modèle et renvoi une liste de string avec les arguments de la commandes
    '''
    def dec_command(self, msg):
        #FAIRE UNE BOUCLE POUR LE BUFFER
        cmd = msg.decode()
        cmd = cmd.replace('\\',' ')
        
        print ("DEC")
        print (cmd)
        print ()
        
        if cmd.startswith("CON "):
            cmd = cmd.split(' ')
            self.CON(cmd[1])
            return cmd

        elif cmd.startswith("MAP "):
            cmd = cmd.split(' ')
            self.model.load_map(cmd[1])
            return cmd

        elif cmd.startswith("MOVE "):
            cmd = cmd.split(' ')
            #self.MOVE(listSocket[sock], cmd[1], cmd[2])
            return cmd

        elif cmd.startswith("A_PLAY "):
            cmd = cmd.split(' ')
            #self.model.add_character(cmd[1])
            return cmd

        elif cmd.startswith("D_PLAY "):
            cmd = cmd.split(' ')
            #self.model.quit(cmd[1])
            return cmd

        elif cmd.startswith("T_BOMB "):
            cmd = cmd.split(' ')
            #self.T_BOMB(cmd[1])
            return cmd

        elif cmd.startswith("A_BOMB "):
            cmd = cmd.split(' ')
           # self.model.drop_bomb(cmd[1])
            return cmd

        elif cmd.startswith("A_FRUIT "):
            cmd = cmd.split(' ')
            self.A_FRUIT(int(cmd[1]), int(cmd[2]), int(cmd[3]))
            return cmd

        elif cmd.startswith("D_FRUIT "):
            cmd = cmd.split(' ')
            #self.D_FRUIT(cmd[1], cmd[2])
            return cmd
        
        elif cmd.startswith("END "):
            cmd = cmd.split(' ')
            return cmd
        
        return None;


    def CON (self, nicknamePlayer):
        #create player
        return;
    
    def A_FRUIT (self, kind, x, y):
        self.model.add_fruit(kind, (x,y))
        return;






################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.port = port;
        self.cmd = Command_Network(model,True)
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM);
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
        self.soc.bind(('', port));
        self.soc.listen(1);
        self.socks = {};
        self.socks[self.soc] = "SERVER";

    '''
    Connection d'un nouveau client, initialise ses champs
    '''
    def clientConnection(self, sockserv):
        newSock, addr= sockserv.accept()
        msg = newSock.recv(4096)
        listcmd = self.cmd.dec_command(msg);
        if (listcmd!=None and listcmd[0] == "CON"):
            self.socks[newSock]= listcmd[1]
            print("New connection")
            print(addr)
            
            # envoyer map, fruits, joueurs, bombes
            self.initMap(newSock);
            self.initFruits(newSock)
            #self.initBombs(newSock)
            #self.initCharacters(newSock)
            newSock.send(self.cmd.enc_command(str("END ")))
        else:
            print ("Error command init new player")
            newSock.close();
            
    '''
    Doit renvoyer aux autres destinataires
    '''
    def re_send(self,sockSender, cmd):
        for sock in self.socks:
            if sock != self.sock and sock != sockSender:
                sock.sendall(cmd)
                
    '''
    Initialise les characters à envoyer
    '''
    def initCharacters(self, s):
        for char in self.cmd.model.characters:
            if (char.nickname == self.socks[s]):
                #is_player = true
                s.send(self.cmd.enc_command(str("A_PLAY "+nickname+" "+"T"+" "+str(char.kind)+" "+ str(char.pos))));
            else:
                s.send(self.cmd.enc_command(str("A_PLAY "+nickname+" "+"F"+" "+str(char.kind)+" "+ str(char.pos))));
                
    '''
    Initialise les fruits à envoyer
    '''  
    def initFruits(self, s):
        for fruit in self.cmd.model.fruits:
            s.send(self.cmd.enc_command(str("A_FRUIT "+str(FRUITS[fruit.kind])+" "+ str(fruit.pos[X])+" "+ str(fruit.pos[Y]))))
        return
    '''
    Initialise les bombs à envoyer
    '''
    def initBombs(self, s):
        for bomb in self.cmd.model.bombs:
            s.send(self.cmd.enc_command(str("A_BOMB "+bomb.pos)));
        return
    
    '''
    Initialise la map à envoyer
    '''        
    def initMap(self, s):
        if len(sys.argv) == 3:
            s.sendall(self.cmd.enc_command(str("MAP "+sys.argv[2])));
        else:
            s.sendall(DEFAULT_MAP.encode());
        return
    
    '''
    Déconnecte un client
    ''' 
    def disconnectClient(self, s):
        self.model.quit(self.socks[s]);
        del self.socks[s];
        s.close()
                      
    # time event

    def tick(self, dt):
        sel = select.select(self.socks, [], [], 0);
        if sel[0]:
            for s in sel[0]:
                if s is self.soc:
                    self.clientConnection(s);
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
        self.host = host;
        self.port = port;
        self.cmd = Command_Network(model,False)
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
        #Connection
        self.soc.send(self.cmd.enc_command(str("CON "+nickname)));
        
        #Decode map + objects + players
        msg = "\\"
        while (len(msg)>0):
            msg = self.soc.recv(64)
            cmd = self.cmd.dec_command(msg)
            
            if (cmd==None or cmd[0]=="END" ):
                break
            
            #self.cmd.model.load_map(self.soc.recv(64).decode());
            
            #Receive objects

            #Receive players       
            #self.receiveCharacters(self.soc);


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
        sel = select.select([self.soc], [], [], 0);
        if sel[0]:
            for s in sel[0]:
                msg = s.recv(4096);
                print (msg)
                if (len(msg) <= 0):
                    print ("Error: Server has been disconnected")
                    s.close();
                    
        self.cmd.model.tick(dt);
        
        return True
