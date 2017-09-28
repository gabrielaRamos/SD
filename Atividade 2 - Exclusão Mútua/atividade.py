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
lock = Lock()
oks = 0
class Exclusao(Thread): # Consome as mensagens recebidas
    def __init__(self ):
        Thread.__init__(self)


    def run(self):
        global lock
        global oks
        solicitacao = list()


        if (len(fila_app) > 0):
            solicitacao = fila_app.pop(0)

            if ((int)(solicitacao[1]) == 1): # Se alguém pediu o recurso

                if (intencao == 0): # E o recurso Não me interessa...
                    e = Enviar(solicitacao[0][1], 0, cont, 2) # enviar OK
                    e.start()

                else: # Caso contrário, se me interessa o recurso
                    if((time_intencao <= (int)(solicitacao[0][0])) or ((time_intencao == (int)(solicitacao[0][0])) and n_processo < (int)(solicitacao[0][1]))):
                        fila_intencao.append(solicitacao[0][1]) #ganhei a disputa, adicionei o perdedor na fila

                        if(n_processo == (int)(solicitacao[0][1])):
                            oks = oks + 1;

                            if(oks == total_processos):
                                ticktacker = TickTacker()
                                ticktacker.start()
                    else: #Perdi a disputa
                        print("Perdi a disputa")
                        e = Enviar(solicitacao[0][1], 0, cont, 2) # enviar OK
                        e.start() # e chora
                        oks = 0
            else: #Se alguem enviou OK, preciso ver se esse OK é para mim.

                if(n_processo == solicitacao[0][1]):

                    oks = oks + 1;
                    if(oks == total_processos):
                        ticktacker = TickTacker()
                        ticktacker.start()





class TickTacker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.timer = random.randrange(2,5)
    def run(self):
        global intencao
        global oks
        global lock
        if(lock.acquire(True,5)):
            print("CONSEGUI A LOCK")
        else:
            print("Como nissin?")
        print("Segurando o recurso! Contagem regressiva: ", end=" ")
        while(self.timer>0): #consumindo recurso
            sys.stdout.flush()
            print( self.timer, end = " ")
            self.timer = self.timer - 1
            time.sleep(1)
        lock.release()
        oks = 0
        intencao = 0
        while(len(fila_intencao) > 0): #passar o recurso adiante
            pid = fila_intencao.pop(0)
            e = Enviar(pid, 0, cont, 2)
            e.start()
            print("tamanho da fila", len(fila_intencao))

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
            mid_solicitaMsg = list()
            mid_solicitaMsg.append(self.mid)
            mid_solicitaMsg.append(self.solicitaMsg)
            fila_app.append(mid_solicitaMsg)
            e = Exclusao()
            e.start()
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
                    serverSocket.listen(1)
                    print ('*** Subindo o Processo de número ', self.num,' no total de ',total_processos,'***')
                    print('*** No ar através da porta: ', serverPort,' ***' )

                    while 1:
                        connectionSocket, addr = serverSocket.accept()

                        try:
                            msg = connectionSocket.recv(64)
                            msg = msg.decode('utf-8') # "pid ack cont"
                            vet = msg.split() # (pid, ack, cont)

                            if(vet[3] == '2' and int(vet[0]) == n_processo):
                                oks = oks + 1
                                print("oks", oks)
                                if(oks == int(total_processos)):
                                    print("UHUL GANHEI ")
                                    ticktacker = TickTacker()
                                    ticktacker.start()

                            if(vet[1] == '1'):
                                # print ("Recebi ack mensagem da mensagem: ", vet[2], " ",vet[0],"da máquina: ", addr)
                                mensagens.insereOrdenado(vet[1], vet[0], vet[2], vet[3])

                            else:
                                # print ("Recebi a mensagem: ", vet[2] ," ", vet[0] ," da máquina: ", addr)
                                e = Enviar(vet[0], 1, vet[2], 0) # (pid ack cont)
                                e.start()
                                # print ("Enviando ack para a mensagem: ", vet[2] ," ", vet[0])
                                mensagens.insereOrdenado(vet[1], vet[0], vet[2], vet[3])
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
                    msg = str(self.pid) + ' ' + str(self.ack) + ' ' + str(self.cont) + ' ' + str(self.solicitaMsg)
                    sock.send(msg.encode())
                    if not self.ack:
                        print ("Enviei a mensagem: ", self.cont ," " ,self.pid , " para ",self.n)

                except Exception as e:
                    print(e)

def menu():
    global n_processo
    global total_processos
    global fila_app
    global mensagens
    global intencao
    global cont
    global time_intencao
    global lock

    mensagens = Mensagens()
    while 1:
        lock.acquire()
        print("Travei a trava")
        print("\n\n")
        print ("Selecione a opçao:")
        print ("1. Solicitar recurso")
        print ("0. Sair")

        opcao = input("Opção: ")
        lock.release()
        print()
        if opcao == '1':
            intencao = 1
            enviar = Enviar(n_processo, 0, cont, 1) #pid ack cont
            enviar.start()
            time.sleep(0.05)

            time_intencao = cont
            oks = 0;
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
    n_processo = int(sys.argv[1])
    total_processos = int(sys.argv[2])
    a = Receber(n_processo)
    a.start()
    time.sleep(0.09)
    menu()

if __name__ == "__main__":
    main()
