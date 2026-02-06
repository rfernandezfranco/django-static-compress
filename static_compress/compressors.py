import gzip
import tempfile

import brotli
from django.core.files.base import ContentFile, File
from zopfli import gzip as zopfli

__all__ = ["BrotliCompressor", "ZlibCompressor", "ZopfliCompressor"]

CHUNK_SIZE = 64 * 1024


class BrotliCompressor:
    extension = "br"

    def compress(self, path, file):
        compressor = brotli.Compressor()
        tmp = tempfile.SpooledTemporaryFile()
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            tmp.write(compressor.process(chunk))
        tmp.write(compressor.finish())
        tmp.seek(0)
        return File(tmp)


class ZlibCompressor:
    extension = "gz"

    def compress(self, path, file):
        tmp = tempfile.SpooledTemporaryFile()
        with gzip.GzipFile(fileobj=tmp, mode="wb") as gz:
            for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
                gz.write(chunk)
        tmp.seek(0)
        return File(tmp)


class ZopfliCompressor:
    extension = "gz"

    def compress(self, path, file):
        return ContentFile(zopfli.compress(file.read()))
