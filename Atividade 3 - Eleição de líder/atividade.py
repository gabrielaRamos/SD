#!/usr/bin/python3
import lamport
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

def Eleicao():
    global n_processo
    global total_processos

    for temp in range (n_processo, total_processos+1):
        lamport.Enviar(temp)

def menu():
    global n_processo
    global total_processos
    global fila_app

    while 1:
        print("\n\n")
        print ("Selecione a opção:")
        print ("1. Fazer eleição")
        print ("0. Sair")

        opcao = input("Opção: ")
        print()
        if opcao == '1':
            enviar = lamport.Enviar(0) #pid ack
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
    n_processo = int(sys.argv[1])
    total_processos = int(sys.argv[2])
    lamport.conf_lamport(n_processo, total_processos)
    a = lamport.Receber(n_processo)
    a.start()
    time.sleep(0.09)
    menu()

if __name__ == "__main__":
    main()
