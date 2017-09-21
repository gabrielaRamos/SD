#!/usr/bin/python3

import sys
from operator import itemgetter, attrgetter, methodcaller
from threading import Thread, Lock
import random
import socket
import os
import time

#globais
fila_app = list()
fila_intencao = list()
cont = 0
total_processos = 0
n_processo = 0
intencao = 0
time_intencao = 0
lock = Lock()

class Exclusao(Thread):
    def __init__(self ):
        Thread.__init__(self)


    def run(self):
        global lock
        solicitacao = list()
        with lock:
            if (len(fila_app) > 0):
                solicitacao = fila_app.pop(0)
                if (solicitacao[1] == 1):
                    if (intencao == 0):
                        e = Enviar(solicitacao[0][1], 0, cont, 1) # enviar OK
                        e.start()
                    else
                        if((time_intencao < (int)solicitacao[0][0]) or ((time_intencao == (int)solicitacao[0][0]) and n_processo < (int)solicitacao[0][1])):
                            fila_intencao.append(solicitacao[0][1])
                        else:
                            e = Enviar(solicitacao[0][1], 0, cont, 1) # enviar OK
                            e.start()


#******************************#
class Mensagem():
    def __init__(self, msg, cont_acks, pid, cont, solicitaMsg):
        if(msg == 0):
            self.msg = False;
        else:
            self.msg = True
        self.acks = int(cont_acks);
        self.mid = list();
        self.mid.append(cont)
        self.mid.append(pid)
        self.solicitaMsg = solicitaMsg

    def tryAdd(self):
        global total_processos
        global fila_app

        if(self.msg == True and self.acks == total_processos):
            fila_app.append(list(self.mid. self.solicitaMsg))
            return 1

class Mensagens():
    def __init__(self):
        self.msg = list() #lista de Mensagens.

    def insereOrdenado(self, ack, pid, cont, solicitaMsg):
        if not self.msg: #se o vetor de mensagens é vazio
            if(ack == 1):
                mensagem = Mensagem( False, ack, pid, cont, solicitaMsg)
            else:
                mensagem = Mensagem( True, ack, pid, cont, solicitaMsg)
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
                    mensagem = Mensagem( False, ack, pid, cont, solicitaMsg)
                else:
                    mensagem = Mensagem( True, ack, pid, cont, solicitaMsg)
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
                                # print ("Recebi ack mensagem da mensagem: ", vet[2], " ",vet[0],"da máquina: ", addr)
                                recursos.insereOrdenado(vet[1], vet[0], vet[2], vet[3] )

                            else:
                                # print ("Recebi a mensagem: ", vet[2] ," ", vet[0] ," da máquina: ", addr)
                                e = Enviar(vet[0], 1, vet[2]) # (pid ack cont)
                                e.start()
                                # print ("Enviando ack para a mensagem: ", vet[2] ," ", vet[0])
                                recursos.insereOrdenado(vet[1], vet[0], vet[2], vet[3])
                                cont = (max(int(vet[2]), cont) + 1)

                        except Exception as e :
                            exec_type, exec_obj, exec_tb = sys.exc_info()
                            print ("Erro!!!", exec_type, exec_tb.tb_lineno,"\n",e)
                            sys.exit(2)

            except Exception as e :
                    print (e)
                    os._exit(1)



class Enviar(Thread):
        def __init__ (self, pid, ack, cont, solicitaMsg = ""):
              Thread.__init__(self)
              global total_processos
              self.total = total_processos
              self.pid = pid
              self.ack = ack
              self.cont = cont
              self.solicitaMsg = solicitaMsg
        def run(self):
            global cont

            for self.n in range (1, self.total+1):

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_address = ('localhost', 12000 + self.n)
                    sock.connect(server_address)
                    msg = str(self.pid) + ' ' + str(self.ack) + ' ' + str(self.cont) + ' 'str(self.solicitaMsg)
                    sock.send(msg.encode())
                    if not self.ack:

                        print ("Enviei a mensagem: ", self.cont ," " ,self.pid , " para todo mundo.")

                except Exception as e:
                    print(e)

def menu():
    global n_processo
    global total_processos
    global fila_app
    global recurso
    global intencao
    global cont
    global time_intencao

    recurso = Mensagens()
    while 1:
        print("\n\n")
        print ("Selecione a opçao:")
        print ("1. Solicitar recurso")
        print ("0. Sair")

        opcao = input("Opção: ")
        print()
        if opcao == '1':

            enviar = Enviar(n_processo, 0, cont) #pid ack cont
            enviar.start()
            time.sleep(0.05)
            intencao = 1
            time_intencao = cont
        elif opcao == '0':
            print("\n\nAdeus amiguinho!")
            os._exit(0)
        else:
            print("\n\n\nOpção Inválida!!!\n")
def main():
    if( len(sys.argv)!=3):
        print("Chamada inválida use: $ python3 atividade.py NUM_PROCESSO TOTAL_PROCESSOS")
        sys.exit(1)
    global n_processo
    global total_processos
    global recursos
    n_processo = int(sys.argv[1])
    total_processos = int(sys.argv[2])
    a = Receber(n_processo)
    a.start()
    time.sleep(0.09)
    menu()

if __name__ == "__main__":
    main()
