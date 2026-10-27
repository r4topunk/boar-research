// The cases native must refuse (-1 -> JS falls back to fzstd): no recorded content size, two frames, garbage, empty,
// and a valid frame must still decode. Uses the system libzstd only to build the inputs.
#include <stdio.h>
#include <string.h>
#include <zstd.h>
#include "../tree/modules/boar-zstd/cpp/boar_zstd.h"
int main(void) {
  char text[4096]; for (int i = 0; i < 4096; i++) text[i] = "boar zstd "[i % 10];
  unsigned char a[8192], b[16384], out[8192]; int fails = 0;
  size_t al = ZSTD_compress(a, sizeof a, text, sizeof text, 3);
  ZSTD_CCtx *c = ZSTD_createCCtx(); ZSTD_CCtx_setParameter(c, ZSTD_c_contentSizeFlag, 0);
  size_t ul = ZSTD_compress2(c, b, sizeof b, text, sizeof text);
  #define CHECK(name, cond) do { int ok = (cond); printf("%-28s %s\n", name, ok ? "ok" : "FAIL"); fails += !ok; } while (0)
  CHECK("valid frame size", boar_zstd_frame_size(a, al) == 4096);
  CHECK("valid frame decodes", boar_zstd_decompress(out, sizeof out, a, al) == 4096 && memcmp(out, text, 4096) == 0);
  CHECK("unknown content size -> -1", boar_zstd_frame_size(b, ul) == -1);
  memcpy(b, a, al); memcpy(b + al, a, al);
  CHECK("two frames -> -1", boar_zstd_frame_size(b, 2 * al) == -1);
  CHECK("garbage -> -1", boar_zstd_frame_size("not zstd at all", 15) == -1);
  CHECK("empty -> -1", boar_zstd_frame_size(a, 0) == -1);
  // The packs' frames carry no checksum (node:zlib default), so a flipped body byte can decode silently, in fzstd too;
  // what native must catch is a broken frame header or a truncated frame.
  memcpy(b, a, al); b[0] ^= 0xff;
  CHECK("bad magic -> -1", boar_zstd_frame_size(b, al) == -1 && boar_zstd_decompress(out, sizeof out, b, al) == -1);
  CHECK("truncated frame -> -1", boar_zstd_frame_size(a, al - 3) == -1 && boar_zstd_decompress(out, sizeof out, a, al - 3) == -1);
  CHECK("too-small dst -> -1", boar_zstd_decompress(out, 100, a, al) == -1);
  printf("version %s, %d failure(s)\n", boar_zstd_version(), fails);
  return fails != 0;
}
