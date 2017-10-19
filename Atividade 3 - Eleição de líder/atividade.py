#!/usr/bin/python3

import sys
from operator import itemgetter, attrgetter, methodcaller
from threading import Thread, Lock
import random
import socket
import os
import time
import signal

#globais
fila_app = list()
total_processos = 0
n_processo = 0
lider= -1
lock = Lock()
lock_fila = Lock()
ganhei = True
lider_alive = False

class Handler(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global lock
        global lock_fila
        global fila_app
        global lider
        global lider_alive
        global n_processo
        global ganhei

        while 1:
            lock_fila.acquire()
            if(len(fila_app)) > 0:
                conteudo = fila_app.pop(0)
                if(conteudo[1] == 'e'):
                    if (int(conteudo[0]) > n_processo):
                        lider = conteudo[0]
                        lider_alive = True
                        ganhei = False
                        #lider ganhou, fico quieto
                    else: # eu sou maior que o lider
                        enviar = Enviar(conteudo[0], 'o') #avisando para ele que eu estou vivo
                        enviar.start()
                        print("O processo ", conteudo[0], " menor do que eu, ta querendo roubar meu lugar...")

                elif(conteudo[1] == 'l'):
                    if (int(conteudo[0]) < n_processo):
                        enviar = Enviar(conteudo[0], 'o') #avisando para ele que eu estou vivo
                        enviar.start()
                        lider = n_processo
                        e = Eleicao()
                        e.start()
                    else:
                        lider = conteudo[0]
                        lider_alive = True
                        print("O líder vivo atual no momento :", conteudo[0])
                else: # se recebi algum 'o'
                    ganhei = False

            lock_fila.release()
            time.sleep(1)

class Receber(Thread):
        def __init__ (self, num):
              Thread.__init__(self)
              self.num = int(num)

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
            global lock_fila
            try:
                msg = self.connection.recv(32)
                msg = msg.decode('utf-8')
                vet = msg.split() # (pid, mensagem)
                lock_fila.acquire()
                lista = list()
                lista.append(vet[0])
                lista.append(vet[1])
                fila_app.append(lista)
                lock_fila.release()

            except Exception as e :
                exec_type, exec_obj, exec_tb = sys.exc_info()
                print ("Erro!!!", exec_type, exec_tb.tb_lineno,"\n",e)
                sys.exit(2)


class Enviar(Thread):
        def __init__ (self, pid, mensagem):
              Thread.__init__(self)
              self.pid = int(pid)
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
                    print("Nao consegui me comunicar com a maquina:", self.pid)


class Eleicao(Thread):
    def __init__ (self):
        Thread.__init__(self)
    def run(self):
        global n_processo
        global total_processos
        global ganhei
        global lock
        global lider
        global lider_alive
        for destinatario in range (int(n_processo)+1, int(total_processos)+1):
            enviar = Enviar(destinatario, "e")
            enviar.start()
        with lock:
            ganhei = True #Sou o líder a menos que provem o contrário
        time.sleep(random.randrange(3,5))
        # ou recebi nada ou recebi algum 'o'
        while(True):

            if(ganhei==True):
                print("Sou líder no momento!")
                for n in range(1, n_processo):
                    enviar = Enviar(n, "l")
                    enviar.start()
                time.sleep(1)
            else:
                print("Tentei realizar o processo de eleição, mas perdi! Líder do momento = ", lider)
                ganhei = False
                break;
                # ganhei = F

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
            pid = 1200 + int(n_processo)

            time.sleep(0.05)

        elif opcao == '0':
            print("\n\nAdeus amiguinho!")

            os._exit(0)
        else:
            print("\n\n\nOpção Inválida!!!\n")
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    if( len(sys.argv)!=3):
        print("Chamada inválida use: $ python3 atividade.py NUM_PROCESSO TOTAL_PROCESSOS")
        sys.exit(1)
    global n_processo
    global total_processos
    global mensagens
    global timeout
    global lock
    global lider
    global lider_alive

    n_processo = int(sys.argv[1])
    total_processos = int(sys.argv[2])

    a = Receber(n_processo)
    a.start()
    h = Handler()
    h.start()

    while 1:
        timeout = random.randrange(3,5)
        while timeout > 0 :
            lock.acquire()
            if lider_alive == True:
                timeout = random.randrange(3,5)
                lider_alive = False
                lider = -1
            else:
                timeout = timeout - 1

            lock.release()
            time.sleep(1)
        e = Eleicao()
        e.start()

if __name__ == "__main__":
    main()
