/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
import java.rmi.Remote;
import java.rmi.RemoteException;

public interface FileProcessor extends Remote{

    public boolean sendFile(String fileName, byte[] data, int i, int byteReaded) throws RemoteException ;
    public void setFileName(String fileName) throws RemoteException;;
    
    
}
