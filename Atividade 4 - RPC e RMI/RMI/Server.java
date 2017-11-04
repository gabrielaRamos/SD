/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.rmi.AlreadyBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Server {
  public static void main(String[] args) {
    try {
    
   // System.setSecurityManager(new RMISecurityManager());
    SendFile transferFile = new SendFile();
    LocateRegistry.createRegistry(12345);
    Registry registry = LocateRegistry.getRegistry(12345);
    registry.bind("SendFile", transferFile);
       
    System.out.println("Server is ready...");
    
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}
