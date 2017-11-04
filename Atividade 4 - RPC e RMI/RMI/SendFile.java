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
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.logging.Level;
import java.util.logging.Logger;

public class SendFile extends UnicastRemoteObject implements FileProcessor {

	private static final long serialVersionUID = 2150067423945685077L;
	private FileOutputStream file;
    private FileInputStream fileInput;
	private String fileName;
	private File f;
	public SendFile() throws RemoteException {
		super();
	}
		
    @Override
	public boolean sendFile(String fileName, byte[] data, int offset, int length) throws RemoteException {
		try {
			file = new FileOutputStream(this.f);
			file.write(data, 0, length);
			
			file.flush();
			return true;
		} catch (IOException e) {
			e.printStackTrace();
		}
		return false;
	}

    @Override
    public void setFileName(String fileName) throws RemoteException {
       this.f = new File(fileName);
    }
}
