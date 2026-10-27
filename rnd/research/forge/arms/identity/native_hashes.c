// Byte-identity, native side: decompresses every block of a pack with the module's own C (boar_zstd.c, which
// includes the vendored decoder) and prints "<id> <out bytes> <sha256>" per block; "-1" marks a block native refuses.
#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <CommonCrypto/CommonDigest.h>
#include "../tree/modules/boar-zstd/cpp/boar_zstd.h"
int main(int argc, char **argv) {
  sqlite3 *db; sqlite3_stmt *st;
  if (sqlite3_open_v2(argv[1], &db, SQLITE_OPEN_READONLY, NULL) != SQLITE_OK) return 2;
  sqlite3_prepare_v2(db, "SELECT id, zdata FROM blocks ORDER BY id", -1, &st, NULL);
  while (sqlite3_step(st) == SQLITE_ROW) {
    long long id = sqlite3_column_int64(st, 0);
    const void *z = sqlite3_column_blob(st, 1); int zl = sqlite3_column_bytes(st, 1);
    int64_t n = boar_zstd_frame_size(z, zl);
    if (n < 0) { printf("%lld -1 -\n", id); continue; }
    unsigned char *out = malloc(n ? n : 1);
    int64_t w = boar_zstd_decompress(out, n, z, zl);
    unsigned char h[32]; CC_SHA256(out, (CC_LONG)(w < 0 ? 0 : w), h);
    printf("%lld %lld ", id, (long long)w); for (int i = 0; i < 32; i++) printf("%02x", h[i]); printf("\n");
    free(out);
  }
  return 0;
}
