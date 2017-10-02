#!/usr/bin/python3
import sys
from operator import itemgetter, attrgetter, methodcaller
from threading import Thread, Lock
import random
import socket
import os
import time
import colorama
from colorama import Fore, Style

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
lock_enviar = Lock()
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
        while 1:
            time.sleep(0.1)
            with lock_a: # Com a lock da fila_app
                if (len(fila_app) > 0): # se tenho alguma mensagem na camada de baixo
                    print(Fore.RED +"INDO PROCESSAR UMA MENSAGEM" + Style.RESET_ALL)
                    u_print = False
                    buffer_temp = fila_app.pop(0) #buffer_temp = list( mid(cont, dest, reme), payload )
                    print("Buffer_temp: ",buffer_temp)
                    if(int(buffer_temp[0][1]) == 0 or int(buffer_temp[0][1]) == n_processo):
                        if ((buffer_temp[1]) == 'q'): # Se alguém pediu o recurso
                            if (intencao == 0): # E o recurso Não me interessa...
                                with lock_cont:
                                    e = Enviar(n_processo, buffer_temp[0][2], 0, cont, 'o') # enviar OK
                                e.start()
                            else: # Caso contrário, se me interessa o recurso
                                if(int(buffer_temp[0][2]) != n_processo): # se eu recebi uma proposta de alguem que não sou eu.
                                    print("Recebi uma proposta, meu tempo de intenção é:",time_intencao," e o do cara é:",str(buffer_temp[0][0]), "Meu número é: ",n_processo," E o dele..: ",str(buffer_temp[0][2]))
                                if((time_intencao < int(buffer_temp[0][0])) or (time_intencao == int(buffer_temp[0][0])
                                 and n_processo <= int(buffer_temp[0][2]))): #se eu ganhei a disputa
                                    if(n_processo != int(buffer_temp[0][2])):
                                        fila_intencao.append(buffer_temp[0][2]) #adiciona o perdedor na fila, se ele não for eu...
                                    else: # se eu ganhei a disputa de mim mesmo:
                                        with lock_oks:
                                            oks = oks + 1
                                            print("Estou somando meu ok", oks)
                                            u_print = False
                                            if(oks == total_processos):
                                                ticktacker = TickTacker()
                                                ticktacker.start()
                                else: #Perdi a disputa
                                    print("Perdi a disputa para o processo: ",buffer_temp[0][2])
                                    u_print = False
                                    with lock_cont:
                                        e = Enviar(n_processo, buffer_temp[0][2], 0, cont, 'o') # enviar OK
                                        print("Enviando ok para o ganhador...")
                                    e.start() # e chora

                        elif(buffer_temp[1] == 'o'):
                            if(n_processo == int(buffer_temp[0][1])):
                                print("Eba recebi um ok de um outro processo para mim!")
                                with lock_oks:
                                    oks = oks + 1;
                                    print("oks", oks)
                                    if(oks == total_processos):
                                        ticktacker = TickTacker()
                                        ticktacker.start()
                    else:
                        print("Ops, a mensagem não era para mim...")
class TickTacker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.timer = random.randrange(5,8)
    def run(self):
        global intencao
        global oks
        global lock_t, lock_cont
        global u_print
        with lock_t:
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

        oks = 0
        intencao = 0
        while(len(fila_intencao) > 0): #passar o recurso adiante
            destinatario = fila_intencao.pop(0)
            with lock_cont:
                e = Enviar(n_processo, destinatario, 0, cont, 'o')
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

        entrega = list()
        entrega.append(self.mid)
        entrega.append(self.payload)
        if(self.payload is not False and self.acks == total_processos):
            with lock_a:
                print("Estou adicionando na fila app: ", entrega)
                fila_app.append(entrega)
            return 1
        elif self.payload is False :
            print("Não consegui adicionar a mensagem porque payload é falso")
        elif (self.acks != total_processos):
            print("Faltam: ", Fore.RED, total_processos - self.acks, Style.RESET_ALL, "Acks para eu subir a mensagem: ", Fore.YELLOW,entrega,Fore.RESET)


class Mensagens():
    def __init__(self):
        self.lista = list() #lista de Mensagens.

    def insereOrdenado(self, destinatario, remetente, ack, cont, payload):
        global fila_app, lock_cont, lock_a
        print("InsereOrdenado: ",destinatario, remetente, ack, cont, payload)
        if not self.lista: #se o vetor de mensagens é vazio
            mensagem = Mensagem( destinatario, remetente, ack, cont, payload)
            self.lista.append(mensagem)
            print("tava vazio, dei append")

        else: # se o vetor não é vazio, insere o ack/mensagem nele
            #criando o message_id
            mid = list()
            mid.append(cont)
            mid.append(destinatario)
            mid.append(remetente)
            achou = False
            for cnt in range (0, len(self.lista)): # Procura entre todas as mensagens
                if(self.lista[cnt].mid[0] == mid[0] and self.lista[cnt].mid[0]): #se mensagem ja é existente [comparo apenas o cont e o remetente]
                    achou = True
                    print("Não estava mais vazio, adicionei no lugar certo")
                    self.lista[cnt].acks += int(ack)
                    if(int(ack) == 0):
                        self.lista[cnt].payload = payload
                    self.lista[cnt].tryAdd()
                    break

            #ainda nao foi adc na lista
            if(not achou):
                print("Não estava vazio, mas adicionei e dei sort")
                mensagem = Mensagem( destinatario, remetente, ack, cont, payload)
                self.lista.append(mensagem)
                self.lista = sorted(self.lista, key = lambda mensagem: mensagem.mid)
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
                print(Fore.GREEN,"Recebi:",Style.RESET_ALL," [para:", vet[0],",de:",vet[1],",ack:",vet[2],",cont:",vet[3],",payload",vet[4],"]")
                with lock_i:
                    mensagens.insereOrdenado(vet[0], vet[1], vet[2], vet[3], vet[4])
                if(vet[2] == '0'): #se recebi mensagem
                    e = Enviar(vet[1], vet[1], 1, vet[3]) # (destinatario_que_agora_é_o_remetente ack cont)
                    e.start() #envio ack para essa mensagem
                    with lock_cont:
                        cont = (max(int(vet[2]), cont) + 1) # e faço lamport no contador

            except Exception as e :
                exec_type, exec_obj, exec_tb = sys.exc_info()
                print ("Erro!!!", exec_type, exec_tb.tb_lineno,"\n",e)
                sys.exit(2)



class Enviar(Thread): #Envia uma mensagem no estilo:  [destinatario, remetente, ack, cont, msg]
        def __init__ (self, remetente, destinatario, ack, cont, payload = "0"): #remetente não vem aqui pq não precisa
              Thread.__init__(self)
              global lock_cont, lock_enviar
              global n_processo
              self.remetente = remetente
              self.destinatario = destinatario
              self.ack = ack
              self.cont = cont
              self.payload = payload

        def run(self):
            global total_processos
            print(Fore.BLUE,"Enviei:",Style.RESET_ALL," [para:",self.destinatario,",de:",self.remetente,",ack:",self.ack,",cont:",self.cont,",payload",self.payload,"]")
            for self.n in range (1, total_processos + 1):
                with lock_enviar:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect(('localhost', 12000 + int(self.n)))
                        msg = str(self.destinatario) + ' ' + str(self.remetente) +' ' + str(self.ack) + ' ' + str(self.cont) + ' ' + str(self.payload)
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
    global lock_cont, lock_t
    global time_intencao
    global u_print
    global leu
    mensagens = Mensagens()

    while 1:
        time.sleep(0.5)
        leu = True
        with lock_t:
            print(Fore.RED +"Selecione a opçao:")
            print(Fore.YELLOW +"1. Solicitar recurso")
            print("0. Sair")
            print(Style.RESET_ALL)
            u_print = True
            leu = False
        if not leu:
            opcao = input("Opção: ")
            leu = True

        print()
        if opcao == '1':
            print("Aguardando por OKs")
            intencao = 1
            oks = 0;
            with lock_cont:
                time_intencao = cont
                enviar = Enviar(n_processo,0, 0, cont, 'q') #destinatario ack cont   dest 0 é broadcast
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
