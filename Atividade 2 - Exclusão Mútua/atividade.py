
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
oks = 0
u_print = False
leu = False

class Exclusao(Thread): # Consome as mensagens recebidas
    def __init__(self ):
        Thread.__init__(self)

    def run(self):
        global lock_t
        global oks
        global time_intencao
        global fila_app
        global n_processo
        global u_print
        solicitacao = list()
        while 1+1 == 2 :
            time.sleep(0.05)
            lock_t.acquire()
            if (len(fila_app) > 0):
                print("INDO PROCESSAR UMA MENSAGEM")
                solicitacao = fila_app.pop(0)
                if ((solicitacao[1]) == 'q'): # Se alguém pediu o recurso
                    if (intencao == 0): # E o recurso Não me interessa...
                        e = Enviar(solicitacao[0][1], 0, cont, 'o') # enviar OK
                        e.start()
                    else: # Caso contrário, se me interessa o recurso
                        print("Recebi uma proposta, mas meu time_intencao é:",time_intencao," e o do cara é:",str(solicitacao[0][0]), "Meu número é: ",n_processo," E o dele..: ",str(solicitacao[0][1]))
                        if((time_intencao < (int)(solicitacao[0][0])) or ((time_intencao == (int)(solicitacao[0][0]))
                         and n_processo <= (int)(solicitacao[0][1]))):
                            if(n_processo != (int)(solicitacao[0][1])):
                                fila_intencao.append(solicitacao[0][1]) #ganhei a disputa, adicionei o perdedor na fila
                            if(n_processo == (int)(solicitacao[0][1])):
                                oks = oks + 1;
                                print("Estou somando meu ok", oks)
                                if(oks == total_processos):
                                    ticktacker = TickTacker()
                                    ticktacker.start()
                        else: #Perdi a disputa
                            print("Perdi a disputa")
                            u_print = False
                            e = Enviar(solicitacao[0][1], 0, cont, 'o') # enviar OK
                            e.start() # e chora

                elif(solicitacao[1] == 'o'):

                    if(n_processo == int(solicitacao[0][1])):
                        oks = oks + 1;
                        print("oks", oks)
                        if(oks == total_processos):
                            ticktacker = TickTacker()
                            ticktacker.start()
            lock_t.release()

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
            pid = fila_intencao.pop(0)
            e = Enviar(pid, 0, cont, 'o')
            e.start()

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
        global lock_a

        if(self.msg == True and self.acks == total_processos):
            mid_solicitaMsg = list()
            mid_solicitaMsg.append(self.mid)
            mid_solicitaMsg.append(self.solicitaMsg)
            # while(not lock_a.acquire()):
                # time.sleep(0.05)
            print("Estou adicionando na fila app")
            fila_app.append(mid_solicitaMsg)
            # lock_a.release()
            return 1

class Mensagens():
    def __init__(self):
        self.msg = list() #lista de Mensagens.

    def insereOrdenado(self, pid, ack, cont, solicitaMsg):
        global fila_app
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
            try:
                msg = self.connection.recv(64)
                msg = msg.decode('utf-8') # "pid ack cont"
                vet = msg.split() # (pid, ack, cont)
                if(vet[1]=='0'):
                    print("Recebi: ", msg)

                if(vet[1] == '1'):
                    # print ("Recebi ack mensagem da mensagem: ", vet[2], " ",vet[0],"da máquina: ", addr)

                    lock_i.acquire()
                    mensagens.insereOrdenado(vet[0], vet[1], vet[2], vet[3])
                    lock_i.release()

                else:
                    e = Enviar(vet[0], 1, vet[2], '0') # (pid ack cont)
                    e.start()
                    # print ("Enviando ack para a mensagem: ", vet[2] ," ", vet[0])
                    lock_i.acquire()
                    mensagens.insereOrdenado(vet[0], vet[1], vet[2], vet[3])
                    lock_i.release()
                    cont = (max(int(vet[2]), cont) + 1)

            except Exception as e :
                exec_type, exec_obj, exec_tb = sys.exc_info()
                print ("Erro!!!", exec_type, exec_tb.tb_lineno,"\n",e)
                sys.exit(2)



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
            if(int(self.ack) != 1):
                print("Enviei: [",self.pid,",",self.solicitaMsg,"]")
            for self.n in range (1, self.total+1):

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(('localhost', 12000 + int(self.n)))
                    msg = str(self.pid) + ' ' + str(self.ack) + ' ' + str(self.cont) + ' ' + str(self.solicitaMsg)
                    sock.send(msg.encode())
                except:
                        print("Falha ao enviar uma mensagem para o processo ", self.pid)

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
            time_intencao = cont
            enviar = Enviar(n_processo, 0, cont, 'q') #pid ack cont
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
