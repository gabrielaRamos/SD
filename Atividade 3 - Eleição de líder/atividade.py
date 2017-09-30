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
total_processos = 0
n_processo = 0
lider= False
lock = Lock()
ganhei = True

class Handler(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global lock
        global fila_app
        global lider
        global n_processo
        global ganhei

        while 1:
            lock.acquire()
            if(len(fila_app)) > 0:
                conteudo = fila_app.pop(0)
                print(conteudo)
                if(conteudo[1] == 'e'):
                    if (int(conteudo[0]) > n_processo):
                        lider = conteudo[0]
                    else:
                        enviar = Enviar(conteudo[0], 'o')
                        enviar.start()
                else:
                    ganhei = False
                    print("Ganheium ok")
            lock.release()
            time.sleep(1)

class Receber(Thread):
        def __init__ (self, num):
              Thread.__init__(self)
              self.num = num

        def run(self):
            serverPort = 12000 + self.num
            global total_processos

            serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

            try:
                    serverSocket.bind(('',serverPort))
                    serverSocket.listen(1)
                    print ('*** Subindo o Processo de número ', self.num,' no total de ',total_processos,'***')
                    print('*** No ar através da porta: ', serverPort,' ***' )

                    while 1:
                        connectionSocket, addr = serverSocket.accept()
                        cliente = TratarCliente(connectionSocket, addr)
                        cliente.start()

            except Exception as e :
                    print (e)
                    os._exit(1)

class TratarCliente(Thread):
        def __init__ (self, connectionSocket, addr):
              Thread.__init__(self)
              self.addr = addr
              self.connection = connectionSocket

        def run(self):
            global fila_app
            try:
                msg = self.connection.recv(32)
                msg = msg.decode('utf-8')
                vet = msg.split() # (pid, mensagem)
                lock.acquire()
                lista = list()
                lista.append(vet[0])
                lista.append(vet[1])
                fila_app.append(lista)
                lock.release()

            except Exception as e :
                exec_type, exec_obj, exec_tb = sys.exc_info()
                print ("Erro!!!", exec_type, exec_tb.tb_lineno,"\n",e)
                sys.exit(2)


class Enviar(Thread):
        def __init__ (self, pid, mensagem):
              Thread.__init__(self)
              self.pid = pid
              self.mensagem = mensagem
        def run(self):
                global n_processo
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_address = ('localhost', 12000 + self.pid)
                    sock.connect(server_address)
                    msg = str(n_processo) + ' ' + str(self.mensagem)
                    sock.send(msg.encode())

                except Exception as e:
                    print(e)


def Eleicao():
    global n_processo
    global total_processos
    global ganhei
    global lock

    for destinatario in range (n_processo+1, total_processos+1):
        enviar = Enviar(destinatario, "e")
        enviar.start()

    time.sleep(random.randrange(3,5))
    lock.acquire()
    if (ganhei == True):
        print("vamos ACABAR logo")
    else:
        print("nao ganhei a eleicao")
        ganhei = True
    lock.release()

def menu():
    global n_processo
    global total_processos
    global fila_app

    while 1:
        print("\n\n")
        print ("Selecione a opção:")
        print ("1. Desabilitar")
        print ("0. Sair")

        opcao = input("Opção: ")
        print()
        if opcao == '1':
            print("MATEUS SEMPRE ERRA")
            time.sleep(0.05)

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
    global mensagens
    global timeout
    global lock
    global lider
    n_processo = int(sys.argv[1])
    total_processos = int(sys.argv[2])

    a = Receber(n_processo)
    a.start()
    h = Handler()
    h.start()

    while 1:
        timeout = random.randrange(2,5)
        while timeout > 0 :
            lock.acquire()
            if lider != False:
                timeout = random.randrange(2,5)
                lider = False
            else:
                timeout = timeout - 1

            lock.release()
            time.sleep(1)

        Eleicao()

    time.sleep(0.09)
    menu()

if __name__ == "__main__":
    main()
