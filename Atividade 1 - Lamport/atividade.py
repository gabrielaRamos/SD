#!/usr/bin/python3

import threading
import sys
#import argparse

def enviar():
    print ("enviando")
def receber():
    print ("recebido")

def menu():
    n_processo = sys.argv[1]
    total_processos = sys.argv[2]
    
    print(n_processo)
    print(total_processos)
    print ("Selecione a opçao")
    print ("1. Enviar mensagem")
    print ("2. Visualizar mensagens recebidas")
    print ("0. Sair")
    opcao = input("Opção: ")

    if opcao == '1':
        enviar()
    elif opcao == '2':
        receber()
    elif opcao == '0':
        sys.exit()
def main():
    # my code here
    menu()

if __name__ == "__main__":
    main()
