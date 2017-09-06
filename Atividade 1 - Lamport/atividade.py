#!/usr/bin/python3

import sys

from threading import Thread
import random
import socket
import os
import time

#globais
fila_app = list()
fila_rec = list()
cont = 0
total_processos = 0
n_processo = 0

class Receber(Thread):
        def __init__ (self, num):
              Thread.__init__(self)
              self.num = num

        def run(self):
            serverPort = 12000 + self.num
            global total_processos
            serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            #serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            try:
                    serverSocket.bind(('',serverPort))
                    serverSocket.listen(1)
                    print ('*** Subindo o Processo de número ', self.num,' no total de ',total_processos,'***')
                    print('*** No ar através da porta: ', serverPort,' ***' )

                    while 1:
                        print ("Esperando Conexoes...")

                        connectionSocket, addr = serverSocket.accept()
                        print ("Conexao estabelecida! Maquina: ", addr)
                        try:
                            msg = connectionSocket.recv(32)
                            msg = msg.decode('utf-8')
                            vet = msg.split()
                            if(vet[1] == '1'):
                                print("Recebi ack")
                            else:
                                e = Enviar(vet[0], 1, vet[2])
                                e.start()
                                print ("Thread para esse cliente subida com sucesso!", msg)
                                global cont
                                cont = (max(int(vet[2]), cont) + 1)


                        except:
                           print ("Erro ao subir uma nova Thread")
                           sys.exit(2)

            except:
                    print ("ERRO!!!!!!!! Porta ",serverPort, " Ja está em uso! Por acaso abriu o mesmo processo duas vezes?")
                    # os._exit(1)



class Enviar(Thread):
        def __init__ (self, pid, ack, cont):
              Thread.__init__(self)
              global total_processos
              self.total = total_processos
              self.pid = pid
              self.ack = ack
              self.cont = cont
        def run(self):
            global cont

            for self.n in range (1, self.total+1):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_address = ('localhost', 12000 + self.n)
                    sock.connect(server_address)
                    msg = str(self.pid) + ' ' + str(self.ack) + ' ' + str(self.cont)
                    sock.send(msg.encode())

                    print ("Mensagem", msg, " enviada")
                except Exception as e:
                    print(e)

def menu():
    global n_processo
    global total_processos
    while 1:
        print ("Selecione a opção:")
        print ("1. Enviar mensagem")
        print ("2. Visualizar mensagens recebidas")
        print ("0. Sair")

        opcao = input("Opção: ")

        if opcao == '1':
            enviar = Enviar(n_processo, 0, cont)
            enviar.start()

        elif opcao == '2':
            print("mateus errou")
        elif opcao == '0':
            print("\n\nAdeus amiguinho!\n")
            os._exit(0)
        else:
            print("\n\n\n\n\nOpção Inválida!!!\n")
def main():
    # my code here
    if( len(sys.argv)!=3):
        print("Chamada inválida use: $ python3 atividade.py NUM_PROCESSO TOTAL_PROCESSOS")
        sys.exit(1)
    global n_processo
    global total_processos
    n_processo = int(sys.argv[1])
    total_processos = int(sys.argv[2])
    a = Receber(n_processo)
    a.start()
    time.sleep(0.05)
    menu()

if __name__ == "__main__":
    main()
