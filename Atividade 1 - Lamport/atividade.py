#!/usr/bin/python3

import threading
import sys

def enviar():
    print ("enviando")
def receber():
    print ("recebido")
    serverPort = 12000 # + pid

    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            serverSocket.bind(('',serverPort))
        except:
            print "Porta ",serverPort, " Ja em uso!"
            sys.exit(1)
        serverSocket.listen(1)
        print ('***Subindo o servidor no ar!***')


        while 1:
            print "Esperando Conexoes..."

            connectionSocket, addr = serverSocket.accept()
            print "Conexao estabelecida! Maquina: ", addr
            try:
               thread.start_new_thread( atender_cliente, (connectionSocket, addr) )
               while(thread_iniciada==0):
                   pass
               print "Thread para esse cliente subida com sucesso!"

            except Exception,e :
               print "Erro ao subir uma nova Thread", str(e)
               sys.exit(2)

def menu():
    if( len(sys.argv)!=3):
        print("Chamada inválida use: $ python3 atividade.py NUM_PROCESSO TOTAL_PROCESSOS")
        sys.exit(1)
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
        sys.exit(0)
def main():
    # my code here
    menu()

if __name__ == "__main__":
    main()
