#include "files.h"

int main (int argc, char **argv)
{
  
  CLIENT *cl;
  int *result_1;
  files fileToTransfer;
  char *fileName;
  FILE *oFile;
  int finished = 0;

  if(argc !=3){
    printf("Como usar: client <hostname> <nome do arquivo>");
    return 0;
  }
  strcpy(fileToTransfer.name, argv[2]);
  if ((oFile = fopen(fileToTransfer.name, "rb")) == NULL) {
    printf("Arquivo nao existente\n");
  } else {
    
    cl = clnt_create(argv[1], FILE_PROG, FILE_VERS, "tcp");
    if (cl == NULL) {
    clnt_pcreateerror (argv[1]);
    exit (1);
    }
    
    while(!finished) {
      fileToTransfer.nBytes = fread(fileToTransfer.conteudo, 1, MAXLEN, oFile);
      
      if ((result_1 = fileproc_1(&fileToTransfer, cl)) == (int *) NULL ){
        printf("%s", clnt_sperror(cl,argv[1]));
      }
      printf("%s\n", fileToTransfer.conteudo);
      if (fileToTransfer.nBytes < MAXLEN) {
        printf("Arquivo tranferido\n");
        finished = 1;

      }
    }

    fclose(oFile);

  }
  
  
  return 0;
}
