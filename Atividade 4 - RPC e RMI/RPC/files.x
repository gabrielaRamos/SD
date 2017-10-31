const MAXLEN = 262144;

struct files{
  char name[256];
  char conteudo[MAXLEN];
  int nBytes;
};

program FILE_PROG {
  version FILE_VERS
  {
      int FILEPROC(files) = 1;
  } = 1;
} = 0x31230000;