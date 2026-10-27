"""Python 3.14 stdlib stand-in for the `zstandard` package (render_prompt.PackDB uses ZstdDecompressor().decompress only).
Import this module before render_prompt when `zstandard` is not installed."""
import sys, types
try:
    import zstandard  # noqa: F401
except ModuleNotFoundError:
    from compression import zstd as _z

    class ZstdDecompressor:
        def decompress(self, data, max_output_size=0):
            return _z.decompress(data)
    sys.modules["zstandard"] = types.SimpleNamespace(ZstdDecompressor=ZstdDecompressor)
