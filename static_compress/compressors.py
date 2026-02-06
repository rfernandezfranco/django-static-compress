import gzip

import brotli
from django.core.files.base import ContentFile
from zopfli import gzip as zopfli

__all__ = ["BrotliCompressor", "ZlibCompressor", "ZopfliCompressor"]


class BrotliCompressor:
    extension = "br"

    def compress(self, path, file):
        return ContentFile(brotli.compress(file.read()))


class ZlibCompressor:
    extension = "gz"

    def compress(self, path, file):
        return ContentFile(gzip.compress(file.read()))


class ZopfliCompressor:
    extension = "gz"

    def compress(self, path, file):
        return ContentFile(zopfli.compress(file.read()))
