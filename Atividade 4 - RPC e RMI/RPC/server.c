#include "files.h"
#include <string.h>
char fileName[256];
FILE *openFile;
long totalLido;

int * fileproc_1_svc(files *inFile, struct svc_req *rqstp) {
	static int transferido;
	char novoArquivo[256] = "novo";
	if (strcmp(fileName, "") == 0) {
		printf("Novo arquivo");
		strcpy(fileName, inFile->name);
		strcat(novoArquivo, fileName);
		openFile = fopen(novoArquivo, "w+");		
	}
	if (strcmp(fileName, inFile->name) == 0){
		fwrite(inFile->conteudo, 1, inFile->nBytes, openFile);
		if (inFile->nBytes < MAXLEN) {
			printf("Arquivo transferido\n");
			fclose(openFile);
			strcpy(fileName, "");
		}
	}
	
return(&transferido);
}
