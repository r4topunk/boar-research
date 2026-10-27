// Native ceiling: libzstd ZSTD_decompress on the exact blocks the app decompressed per question (blobs.bin + blobs.json order).
// Prints per-question ms (best of REPS passes) so the JS side can be compared question by question.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <zstd.h>
static double now_ms(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec*1e3+t.tv_nsec/1e6; }
int main(int argc,char**argv){
  FILE*f=fopen("blobs.bin","rb"); fseek(f,0,SEEK_END); long n=ftell(f); fseek(f,0,SEEK_SET);
  unsigned char*buf=malloc(n); fread(buf,1,n,f); fclose(f);
  int cap=8192,nb=0; unsigned char**bp=malloc(cap*sizeof*bp); size_t*bl=malloc(cap*sizeof*bl);
  for(long o=0;o<n;){ unsigned len; memcpy(&len,buf+o,4); bp[nb]=buf+o+4; bl[nb]=len; nb++; o+=4+len; }
  // per-question index lists from blobs.idx (written by the Python helper: one line per question, space-separated)
  FILE*q=fopen("blobs.idx","r"); char line[1<<16]; int qn=0; double tot=0;
  void*out=malloc(1<<22); ZSTD_DCtx*dctx=ZSTD_createDCtx();
  while(fgets(line,sizeof line,q)){
    int ids[4096],k=0; for(char*t=strtok(line," \n");t;t=strtok(NULL," \n")) ids[k++]=atoi(t);
    double best=1e9; size_t outb=0;
    for(int r=0;r<5;r++){ double t0=now_ms(); outb=0;
      for(int i=0;i<k;i++){ size_t z=ZSTD_decompressDCtx(dctx,out,1<<22,bp[ids[i]],bl[ids[i]]); if(ZSTD_isError(z)){fprintf(stderr,"err %s\n",ZSTD_getErrorName(z));return 1;} outb+=z; }
      double dt=now_ms()-t0; if(dt<best)best=dt; }
    printf("%d %.3f %zu\n",qn++,best,outb); tot+=best;
  }
  fprintf(stderr,"libzstd %s: %d questions, total %.1f ms\n",ZSTD_versionString(),qn,tot);
}
