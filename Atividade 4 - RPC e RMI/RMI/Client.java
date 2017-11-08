/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Client {
  private FileProcessor fileProcessor;

  public static void main(String[] args) throws FileNotFoundException, IOException {

	System.setProperty("java.rmi.server.hostname","200.9.84.166");

try {

      Client client = new Client();
      Registry registry = LocateRegistry.getRegistry("200.9.84.166");
      client.fileProcessor = (FileProcessor) registry.lookup("SendFile");


      String fileName = "";

      fileName = args[0];

      File file = new File(fileName);
      if (!file.exists()) {
        System.out.println("File not found!");
        return;
      }

      client.fileProcessor.setFileName("novo" + fileName);
      FileInputStream fileInputStream = new FileInputStream(file);
      int byteReaded = 0;
      byte[] data = new byte[1048576];
      long tempoInicial = System.currentTimeMillis();

      while ((byteReaded = fileInputStream.read(data)) != -1) {
        client.fileProcessor.sendFile(fileName, data, 0, byteReaded);
      }
	  long tempoFinal = System.currentTimeMillis();
      System.out.println("Enviado com sucesso");
	  System.out.printf("Tempo para transferencia:" + (float)(tempoFinal - tempoInicial)/100);
      fileInputStream.close();

    } catch (RemoteException | NotBoundException e) {
      e.printStackTrace();
    }
  }
}
