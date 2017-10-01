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
obtive = 0
time_intencao = 0
lock_a = Lock()
lock_t = Lock()
lock_i = Lock()
lock_cont = Lock()
lock_oks = Lock()
oks = 0
u_print = False
leu = False

class Exclusao(Thread): # Consome as mensagens recebidas
    def __init__(self ):
        Thread.__init__(self)

    def run(self):
        global lock_a, lock_cont, lock_oks # Travas, muitas travas
        global oks # Número de oks que o processo recebeu
        global time_intencao # Momento em que o processo decidiu que quer o recurso (se quiser)
        global fila_app # Fila de mensagens recebida do lamport
        global n_processo # Meu número :)
        global u_print # Flag para saber se o último print veio do menu
        buffer_temp = list() #  mensagem recolhida da fila de mensagens da camada de baixo.
        while 1: #buffer_temp = list( mid(cont, dest, reme), payload )
            time.sleep(0.05)
            with lock_a: # Com a lock da fila_app
                if (len(fila_app) > 0): # se tenho alguma mensagem na camada de baixo
                    # print("INDO PROCESSAR UMA MENSAGEM")
                    buffer_temp = fila_app.pop(0) # pego ela
                    if ((buffer_temp[1]) == 'q'): # Se alguém pediu o recurso
                        if (intencao == 0): # E o recurso Não me interessa...
                            lock_cont.acquire()
                            e = Enviar(buffer_temp[0][2], 0, cont, 'o') # enviar OK
                            lock_cont.release()
                            e.start()
                        else: # Caso contrário, se me interessa o recurso
                            print("Recebi uma proposta, mas meu time_intencao é:",time_intencao," e o do cara é:",str(buffer_temp[0][0]), "Meu número é: ",n_processo," E o dele..: ",str(buffer_temp[0][2]))
                            if((time_intencao < int(buffer_temp[0][0])) or (time_intencao == int(buffer_temp[0][0])
                             and n_processo <= int(buffer_temp[0][2]))):
                                if(n_processo != int(buffer_temp[0][2])):
                                    fila_intencao.append(buffer_temp[0][2]) #ganhei a disputa, adicionei o perdedor na fila
                                else: # se o 'q' é meu:
                                    with lock_oks:
                                        oks = oks + 1
                                        print("Estou somando meu ok", oks)
                                        if(oks == total_processos):
                                            ticktacker = TickTacker()
                                            ticktacker.start()
                            else: #Perdi a disputa
                                print("Perdi a disputa")
                                u_print = False
                                with lock_cont:
                                    e = Enviar(buffer_temp[0][2], 0, cont, 'o') # enviar OK
                                e.start() # e chora

                    elif(buffer_temp[1] == 'o'):
                        if(n_processo == int(buffer_temp[0][2])):
                            with lock_oks:
                                oks = oks + 1;
                                print("oks", oks)
                                if(oks == total_processos):
                                    ticktacker = TickTacker()
                                    ticktacker.start()

class TickTacker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.timer = random.randrange(5,8)
    def run(self):
        global intencao
        global oks
        global lock_t
        global u_print
        lock_t.acquire()
        if(u_print == True):
            print("\n\n")
            u_print = False
        print("Segurando o recurso! Contagem regressiva: ", end=" ")
        while(self.timer>0): #consumindo recurso
            sys.stdout.flush()
            print( self.timer, end = " ")
            self.timer = self.timer - 1
            time.sleep(1)
        print("",flush=True)
        print("Liberei recurso")
        lock_t.release()

        oks = 0
        intencao = 0
        while(len(fila_intencao) > 0): #passar o recurso adiante
            destinatario = fila_intencao.pop(0)
            e = Enviar(destinatario, 0, cont, 'o')
            e.start()

class Mensagem():
    def __init__(self, destinatario, remetente, ack, cont, payload=False):
        self.payload = payload; #conteúdo da mensagem.
        self.acks = int(ack) #0 ou 1
        self.mid = list();
        self.mid.append(cont)
        self.mid.append(destinatario)
        self.mid.append(remetente)
        self.payload = payload

    def tryAdd(self):
        global total_processos
        global fila_app
        global lock_a

        if(self.payload is not False and self.acks == total_processos):
            entrega = list()
            entrega.append(self.mid)
            entrega.append(self.payload)
            with lock_a:
                print("Estou adicionando na fila app")
                fila_app.append(entrega)
            return 1

class Mensagens():
    def __init__(self):
        self.lista = list() #lista de Mensagens.
        self.lista = list() #lista de Mensagens.

    def insereOrdenado(self, destinatario, remetente, ack, cont, payload):
        global fila_app, lock_cont, lock_a
        if not self.lista: #se o vetor de mensagens é vazio
            mensagem = Mensagem( destinatario, remetente, ack, cont, payload)
            self.lista.append(mensagem)
            self.lista.append(mensagem)

        else: # se o vetor não é vazio, insere o ack/mensagem nele
            #criando o message_id
            mid = list()
            mid.append(cont)
            mid.append(destinatario)
            mid.append(remetente)
            achou = False
            for cnt in range (0, len(self.lista)): # Procura entre todas as mensagens
                if(self.lista[cnt].mid == mid): #se mensagem ja é existente
                    achou = True
                    self.lista[cnt].acks += int(ack)
                    if(self.lista[cnt].payload is False):
                        self.lista[cnt].payload = payload
                    self.lista[cnt].tryAdd()
                    break

            #ainda nao foi adc na lista
            if(not achou):
                mensagem = Mensagem( destinatario, remetente, ack, cont, payload)
                self.msg.append(mensagem)
                self.msg = sorted(self.msg, key = lambda mensagem: mensagem.mid)
                mensagem.tryAdd()

class Receber(Thread):
        def __init__ (self, num):
              Thread.__init__(self)
              self.num = num

        def run(self):
            serverPort = 12000 + self.num
            global total_processos
            global n_processo
            global cont
            global oks
            serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

            try:
                    serverSocket.bind(('',serverPort))
                    serverSocket.listen(100)
                    print ('*** Subindo o Processo de número ', self.num,' no total de ',total_processos,'***')
                    print('*** No ar através da porta: ', serverPort,' ***' )

                    while 1:
                        connectionSocket, addr = serverSocket.accept()
                        TratarCliente(connectionSocket, addr).start()

            except Exception as e :
                    print (e)
                    os._exit(1)

class TratarCliente(Thread):
        def __init__ (self, connectionSocket, addr):
              Thread.__init__(self)
              self.addr = addr
              self.connection = connectionSocket

        def run(self):

            global total_processos
            global n_processo
            global cont
            global oks
            global lock_i
            global lock_cont
            try:
                msg = self.connection.recv(64)
                msg = msg.decode('utf-8')
                vet = msg.split() # (destinatario(talvez_eu), remetente, ack, cont, mensagem )
                if(vet[2] == '1'): # se recebi ack
                    lock_i.acquire()
                    mensagens.insereOrdenado(vet[0], vet[1], vet[2], vet[3], vet[4])
                    lock_i.release()

                else: #se recebi mensagem
                    print("Recebi: ", msg)
                    e = Enviar(vet[0], 1, vet[2]) # (destinatario ack cont)
                    e.start()
                    lock_i.acquire()
                    mensagens.insereOrdenado(vet[0], vet[1], vet[2], vet[3], vet[4])
                    lock_i.release()
                    lock_cont.acquire()
                    cont = (max(int(vet[2]), cont) + 1)
                    lock_cont.release()

            except Exception as e :
                exec_type, exec_obj, exec_tb = sys.exc_info()
                print ("Erro!!!", exec_type, exec_tb.tb_lineno,"\n",e)
                sys.exit(2)



class Enviar(Thread): #Envia uma mensagem no estilo:  [destinatario, remetente, ack, cont, msg]
        def __init__ (self, destinatario, ack, cont, payload = ""): #remetente não vem aqui pq não precisa
              Thread.__init__(self)
              global lock_cont
              self.destinatario = destinatario
              self.ack = ack
              lock_cont.acquire()
              self.cont = cont
              lock_cont.release()
              self.payload = payload

        def run(self):
            global n_processo
            global total_processos
            if(int(self.ack) != 1):
                print("Enviei: [",self.destinatario,",",self.payload,"]")
            for self.n in range (1, total_processos):

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(('localhost', 12000 + int(self.n)))
                    msg = str(self.destinatario) + ' ' + str(n_processo) +' ' + str(self.ack) + ' ' + str(self.cont) + ' ' + str(self.payload)
                    sock.send(msg.encode())
                except:
                        print("Falha ao enviar uma mensagem para o processo ", self.destinatario)

class verifica(Thread):
    def __init__ (self):
          Thread.__init__(self)

    def run(self):
        global leu
        global u_print
        global lock_t
        while 1:
            timer = 1
            while(timer > 0):
                time.sleep(0.1)
                timer = timer - 0.1
            if(leu != True and u_print!= True and lock_t.acquire()):

                print ("\nSelecione a opçao:")
                print ("1. Solicitar recurso")
                print ("0. Sair")
                print ("Opção", end = ":", flush=True)
                u_print = True
                lock_t.release()
def menu():
    global n_processo
    global total_processos
    global fila_app
    global mensagens
    global intencao
    global cont
    global lock_cont
    global time_intencao
    global lock_t
    global u_print
    global leu
    mensagens = Mensagens()

    while 1:
        time.sleep(0.5)
        if(lock_t.acquire()):
            print ("Selecione a opçao:")
            print ("1. Solicitar recurso")
            print ("0. Sair")
            u_print = True
            lock_t.release()
            leu = False
            opcao = input("Opção: ")
            leu = True

        print()
        if opcao == '1':
            print("Aguardando por OKs")
            intencao = 1
            oks = 0;
            lock_cont.acquire()
            time_intencao = cont
            enviar = Enviar(n_processo, 0, cont, 'q') #pid ack cont
            lock_cont.release()
            enviar.start()
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
    n_processo = int(sys.argv[1])
    total_processos = int(sys.argv[2])
    a = Receber(n_processo)
    a.start()
    e = Exclusao()
    e.start()
    time.sleep(0.09)
    v = verifica()
    v.start()
    menu()

if __name__ == "__main__":
    main()
