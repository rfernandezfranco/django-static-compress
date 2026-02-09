import gzip
import unittest
from io import BytesIO
from unittest.mock import patch

import brotli
from django.core.exceptions import ImproperlyConfigured

from static_compress.compressors import (
    DEFAULT_STREAM_MAX_SIZE,
    BrotliCompressor,
    ZlibCompressor,
    ZopfliCompressor,
    _get_stream_max_size,
)

content = b"a" * 100


class ZopfliCompressorTestCase(unittest.TestCase):
    def test_compress(self):
        file = BytesIO(content)

        compressor = ZopfliCompressor()
        out = compressor.compress("", file)
        try:
            self.assertGreater(out.size, 0)
            self.assertLessEqual(out.size, len(content))

            result = gzip.decompress(out.read())
            self.assertEqual(result, content)
        finally:
            out.close()


class BrotliCompressorTestCase(unittest.TestCase):
    def test_compress(self):
        file = BytesIO(content)

        compressor = BrotliCompressor()
        out = compressor.compress("", file)
        try:
            self.assertGreater(out.size, 0)
            self.assertLessEqual(out.size, len(content))

            result = brotli.decompress(out.read())
            self.assertEqual(result, content)
        finally:
            out.close()


class ZlibCompressorTestCase(unittest.TestCase):
    def test_compress(self):
        file = BytesIO(content)

        compressor = ZlibCompressor()
        out = compressor.compress("", file)
        try:
            self.assertGreater(out.size, 0)
            self.assertLessEqual(out.size, len(content))

            result = gzip.decompress(out.read())
            self.assertEqual(result, content)
        finally:
            out.close()


class _DummySettings:
    def __init__(
        self,
        *,
        configured=True,
        value=DEFAULT_STREAM_MAX_SIZE,
        raise_on_configured=False,
    ):
        self._configured = configured
        self.STATIC_COMPRESS_STREAM_MAX_SIZE = value
        self._raise_on_configured = raise_on_configured

    @property
    def configured(self):
        if self._raise_on_configured:
            raise ImproperlyConfigured("settings are not configured")
        return self._configured


class StreamMaxSizeTestCase(unittest.TestCase):
    def test_stream_max_size_invalid_value_falls_back(self):
        dummy = _DummySettings(value="invalid")
        with patch("django.conf.settings", dummy):
            self.assertEqual(_get_stream_max_size(), DEFAULT_STREAM_MAX_SIZE)

    def test_stream_max_size_negative_clamped_to_zero(self):
        dummy = _DummySettings(value=-10)
        with patch("django.conf.settings", dummy):
            self.assertEqual(_get_stream_max_size(), 0)

    def test_stream_max_size_improperly_configured_falls_back(self):
        dummy = _DummySettings(raise_on_configured=True)
        with patch("django.conf.settings", dummy):
            self.assertEqual(_get_stream_max_size(), DEFAULT_STREAM_MAX_SIZE)
