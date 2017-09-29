#!/usr/bin/python3

import sys
from operator import itemgetter, attrgetter, methodcaller
from threading import Thread
import random
import socket
import os
import time

#globais
fila_app = list()
cont = 0
total_processos = 0
n_processo = 0

class Mensagem():
    def __init__(self, msg, cont_acks, pid, cont):
        if(msg == 0):
            self.msg = False;
        else:
            self.msg = True
        self.acks = int(cont_acks);
        self.mid = list();
        self.mid.append(cont)
        self.mid.append(pid)

    def tryAdd(self):
        global total_processos
        global fila_app

        if(self.msg == True and self.acks == total_processos):
            fila_app.append(self.mid)
            return 1

class Mensagens():
    def __init__(self):
        self.msg = list() #lista de Mensagens.

    def insereOrdenado(self, ack, pid, cont):
        if not self.msg: #se o vetor de mensagens é vazio
            if(ack == 1):
                mensagem = Mensagem( False, ack, pid, cont)
            else:
                mensagem = Mensagem( True, ack, pid, cont)
            self.msg.append(mensagem)

        else: # se o vetor não é vazio, insere o ack/mensagem nele
            #criando o message_id
            mid = list()
            mid.append(cont)
            mid.append(pid)
            flag = 0
            cnt = 0
            global fila_app
            while(cnt < len(self.msg)):
                if(self.msg[cnt].mid == mid):
                    flag = True #se mensagem ja é existente
                    break
                cnt+=1

            #essa mensagem ja foi adc na lista
            if(flag == True):
                self.msg[cnt].acks += int(ack)
                if(self.msg[cnt].msg == False and ack == 0):
                    self.msg[cnt].msg = True

                self.msg[cnt].tryAdd()

            #ainda nao foi adc na lista
            else:
                if(ack == 1):
                    mensagem = Mensagem( False, ack, pid, cont)
                else:
                    mensagem = Mensagem( True, ack, pid, cont)
                self.msg.append(mensagem)
                #na ultima posicao
                self.msg[-1].acks += int(ack)
                self.msg = sorted(self.msg, key = lambda mensagem: mensagem.mid)
                cnt = 0
                while(cnt < len(self.msg)):
                    if(self.msg[cnt].mid == mid):
                        break
                    cnt += 1

                self.msg[cnt].tryAdd()


    def imprimeMsg(self):
        global fila_app

        for i in range(0,len(fila_app)):
            print (fila_app[i][0] , "\t\t" , fila_app[i][1])


class Receber(Thread):
        def __init__ (self, num):
              Thread.__init__(self)
              self.num = num

        def run(self):
            serverPort = 12000 + self.num
            global total_processos
            global cont
            serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

            try:
                    serverSocket.bind(('',serverPort))
                    serverSocket.listen(1)
                    print ('*** Subindo o Processo de número ', self.num,' no total de ',total_processos,'***')
                    print('*** No ar através da porta: ', serverPort,' ***' )

                    while 1:
                        connectionSocket, addr = serverSocket.accept()

                        try:
                            msg = connectionSocket.recv(32)
                            msg = msg.decode('utf-8') # "pid ack cont"
                            vet = msg.split() # (pid, ack, cont)
                            if(vet[1] == '1'):
                                print ("Recebi ack mensagem da mensagem: ", vet[2], " ",vet[0],"da máquina: ", addr)
                                #mensagens.insereOrdenado(vet[1], vet[0], vet[2], vet[3])

                            else:
                                print ("Recebi a mensagem: ", vet[2] ," ", vet[0] ," da máquina: ", addr)
                                e = Enviar_interno(vet[0], 1, vet[2], vet[3]) # (pid ack cont)
                                e.start()
                                print ("Enviando ack para a mensagem: ", vet[2] ," ", vet[0])
                                #mensagens.insereOrdenado(vet[1], vet[0], vet[2], vet[3])
                                cont = (max(int(vet[2]), cont) + 1)

                        except Exception as e :
                            exec_type, exec_obj, exec_tb = sys.exc_info()
                            print ("Erro!!!", exec_type, exec_tb.tb_lineno,"\n",e)
                            sys.exit(2)

            except Exception as e :
                    print (e)
                    os._exit(1)

def conf_lamport(n_proc, total_proc):
    global n_processo
    global total_processos
    n_processo = n_proc
    total_processos = total_proc
    print(n_processo, total_processos)


def Enviar(mensagem):
    enviar = Enviar_interno(n_processo, 0, cont, mensagem) #pid ack cont

    enviar.start()

class Enviar_interno(Thread):
        def __init__ (self, pid, ack, cont, mensagem):
              Thread.__init__(self)
              global total_processos
              self.total = total_processos
              self.pid = pid
              self.ack = ack
              self.cont = cont
              self.mensagem = mensagem
        def run(self):
            global cont

            for self.n in range (1, self.total+1):

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_address = ('localhost', 12000 + self.n)
                    sock.connect(server_address)
                    msg = str(self.pid) + ' ' + str(self.ack) + ' ' + str(self.cont) + ' ' + str(self.mensagem)
                    sock.send(msg.encode())
                    print("aqui")
                    if not self.ack:

                        print ("Enviei a mensagem: ", self.cont ," " ,self.pid , " para todo mundo.")

                except Exception as e:
                    print(e)
