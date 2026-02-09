import gzip
import tempfile

import brotli
from django.core.files.base import ContentFile, File
from zopfli import gzip as zopfli

__all__ = ["BrotliCompressor", "ZlibCompressor", "ZopfliCompressor"]

CHUNK_SIZE = 64 * 1024
DEFAULT_STREAM_MAX_SIZE = 1 * 1024 * 1024


def _get_stream_max_size():
    try:
        from django.conf import settings
    except Exception:
        return DEFAULT_STREAM_MAX_SIZE
    if not settings.configured:
        return DEFAULT_STREAM_MAX_SIZE
    return getattr(settings, "STATIC_COMPRESS_STREAM_MAX_SIZE", DEFAULT_STREAM_MAX_SIZE)


class BrotliCompressor:
    extension = "br"

    def compress(self, path, file):
        compressor = brotli.Compressor()
        tmp = tempfile.SpooledTemporaryFile(max_size=_get_stream_max_size())
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            tmp.write(compressor.process(chunk))
        tmp.write(compressor.finish())
        tmp.seek(0)
        return File(tmp)


class ZlibCompressor:
    extension = "gz"

    def compress(self, path, file):
        tmp = tempfile.SpooledTemporaryFile(max_size=_get_stream_max_size())
        with gzip.GzipFile(fileobj=tmp, mode="wb") as gz:
            for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
                gz.write(chunk)
        tmp.seek(0)
        return File(tmp)


class ZopfliCompressor:
    extension = "gz"

    def compress(self, path, file):
        return ContentFile(zopfli.compress(file.read()))
