import os
import tempfile
from pathlib import Path
import gzip
import json

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import Storage
from django.utils import timezone

from django.test import SimpleTestCase
from django.core.management import call_command


class PathlessBaseStorage(Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._files = {}
        self._mtimes = {}

    def path(self, name):
        raise NotImplementedError

    def _open(self, name, mode="rb"):
        return ContentFile(self._files[name])

    def _save(self, name, content):
        data = content.read()
        self._files[name] = data
        self._mtimes[name] = timezone.now()
        return name

    def delete(self, name):
        self._files.pop(name, None)
        self._mtimes.pop(name, None)

    def exists(self, name):
        return name in self._files

    def size(self, name):
        return len(self._files[name])

    def get_modified_time(self, name):
        return self._mtimes[name]


class CollectStaticTest(SimpleTestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def assertFileExist(self, path):
        self.assertTrue(Path(path).exists(), "File {} should exists".format(path))

    def assertFileNotExist(self, path):
        self.assertFalse(Path(path).exists(), "File {} shouldn't exists".format(path))

    def assertStaticFiles(self):
        for file in ["milligram.css", "system.js", "speaker.svg"]:
            self.assertFileExist(self.temp_dir_path / file)
            self.assertFileExist(self.temp_dir_path / (file + ".gz"))
            self.assertFileExist(self.temp_dir_path / (file + ".br"))

        self.assertFileExist(self.temp_dir_path / "not_compressed.txt")

        for file in ["not_compressed.txt.gz", "not_compressed.txt.br"]:
            self.assertFileNotExist(self.temp_dir_path / file)

        for file in ("too_small.js.gz", "too_small.js.br"):
            self.assertFileNotExist(self.temp_dir_path / file)

    def assertManifestStaticFiles(self):
        manifest = json.loads((self.temp_dir_path / "staticfiles.json").read_text())
        hashed_files = manifest["paths"]

        for file in ("milligram.css", "system.js", "speaker.svg"):
            hashed = hashed_files[file]
            self.assertFileExist(self.temp_dir_path / hashed)
            self.assertFileExist(self.temp_dir_path / (hashed + ".gz"))
            self.assertFileExist(self.temp_dir_path / (hashed + ".br"))

        hashed_not_compressed = hashed_files["not_compressed.txt"]
        self.assertFileExist(self.temp_dir_path / hashed_not_compressed)
        self.assertFileNotExist(self.temp_dir_path / (hashed_not_compressed + ".gz"))
        self.assertFileNotExist(self.temp_dir_path / (hashed_not_compressed + ".br"))

        hashed_too_small = hashed_files["too_small.js"]
        self.assertFileExist(self.temp_dir_path / hashed_too_small)
        self.assertFileNotExist(self.temp_dir_path / (hashed_too_small + ".gz"))
        self.assertFileNotExist(self.temp_dir_path / (hashed_too_small + ".br"))

    def test_collectstatic_static(self):
        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
            STATIC_COMPRESS_MIN_SIZE_KB=1,
            STATIC_ROOT=self.temp_dir.name,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)

            self.assertStaticFiles()

    def test_collectstatic_manifest(self):
        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedManifestStaticFilesStorage"}},
            STATIC_COMPRESS_MIN_SIZE_KB=1,
            STATIC_ROOT=self.temp_dir.name,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)

            for file in [
                "milligram.css",
                "system.js",
                "not_compressed.txt",
                "speaker.svg",
                "staticfiles.json",
            ]:
                self.assertFileExist(self.temp_dir_path / file)
                self.assertFileNotExist(self.temp_dir_path / (file + ".gz"))
                self.assertFileNotExist(self.temp_dir_path / (file + ".br"))

            self.assertManifestStaticFiles()

    def test_collectstatic_only_gz(self):
        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
            STATIC_COMPRESS_MIN_SIZE_KB=1,
            STATIC_COMPRESS_METHODS=["gz"],
            STATIC_ROOT=self.temp_dir.name,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)
            for file in ["milligram.css", "system.js", "speaker.svg"]:
                self.assertFileExist(self.temp_dir_path / file)
                self.assertFileExist(self.temp_dir_path / (file + ".gz"))
                self.assertFileNotExist(self.temp_dir_path / (file + ".br"))

            self.assertFileExist(self.temp_dir_path / "not_compressed.txt")
            self.assertFileNotExist(self.temp_dir_path / "not_compressed.txt.gz")

    def test_collectstatic_changed_file_ext(self):
        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
            STATIC_COMPRESS_MIN_SIZE_KB=1,
            STATIC_COMPRESS_FILE_EXTS=("js", "css"),
            STATIC_ROOT=self.temp_dir.name,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)
            for file in ("milligram.css", "system.js"):
                self.assertFileExist(self.temp_dir_path / file)
                self.assertFileExist(self.temp_dir_path / (file + ".gz"))
                self.assertFileExist(self.temp_dir_path / (file + ".br"))

            self.assertFileExist(self.temp_dir_path / "speaker.svg")
            self.assertFileNotExist(self.temp_dir_path / "speaker.svg.gz")

    def test_collectstatic_empty_file_ext(self):
        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
            STATIC_COMPRESS_MIN_SIZE_KB=1,
            STATIC_COMPRESS_FILE_EXTS=[],
            STATIC_ROOT=self.temp_dir.name,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)
            for file in ("milligram.css", "system.js", "speaker.svg"):
                self.assertFileExist(self.temp_dir_path / file)
                self.assertFileNotExist(self.temp_dir_path / (file + ".gz"))
                self.assertFileNotExist(self.temp_dir_path / (file + ".br"))

    def test_collectstatic_not_keep_original(self):
        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
            STATIC_COMPRESS_MIN_SIZE_KB=1,
            STATIC_COMPRESS_KEEP_ORIGINAL=False,
            STATIC_ROOT=self.temp_dir.name,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)
            for file in ("milligram.css", "system.js", "speaker.svg"):
                self.assertFileNotExist(self.temp_dir_path / file)
                self.assertFileExist(self.temp_dir_path / (file + ".gz"))
                self.assertFileExist(self.temp_dir_path / (file + ".br"))

    def test_min_size_overrides_keep_original(self):
        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
            STATIC_COMPRESS_MIN_SIZE_KB=1000,
            STATIC_COMPRESS_KEEP_ORIGINAL=False,
            STATIC_ROOT=self.temp_dir.name,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)
            for file in ("milligram.css", "system.js", "speaker.svg"):
                self.assertFileExist(self.temp_dir_path / file)
                self.assertFileNotExist(self.temp_dir_path / (file + ".gz"))
                self.assertFileNotExist(self.temp_dir_path / (file + ".br"))

    def test_collectstatic_with_zlib(self):
        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
            STATIC_COMPRESS_MIN_SIZE_KB=1,
            STATIC_COMPRESS_METHODS=["gz+zlib", "br"],
            STATIC_ROOT=self.temp_dir.name,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)

            self.assertStaticFiles()

    def test_collectstatic_twice_replace(self):
        with tempfile.TemporaryDirectory() as static_dir:
            with self.settings(
                STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
                STATIC_COMPRESS_MIN_SIZE_KB=1,
                STATIC_COMPRESS_METHODS=["gz+zlib"],
                STATIC_ROOT=self.temp_dir.name,
                STATICFILES_DIRS=[static_dir],
            ):
                output_file_path = self.temp_dir_path / "test.js"
                compressed_file_path = self.temp_dir_path / "test.js.gz"

                static_file = Path(static_dir) / "test.js"
                with static_file.open("wb") as fp:
                    fp.write(b"a" * 5000)

                call_command("collectstatic", interactive=False, verbosity=0)

                self.assertFileExist(output_file_path)
                self.assertFileExist(compressed_file_path)

                # Fake that the file has been written long ago
                os.utime(output_file_path, times=(1, 1))
                os.utime(compressed_file_path, times=(1, 1))

                expected_content = b"b" * 5000
                with static_file.open("wb") as fp:
                    fp.write(expected_content)

                call_command("collectstatic", interactive=False, verbosity=0)

                self.assertEqual(output_file_path.read_bytes(), expected_content)

                with compressed_file_path.open("rb") as fp:
                    self.assertEqual(gzip.open(fp).read(), expected_content)

    def test_collectstatic_delete_shrunken_files(self):
        with tempfile.TemporaryDirectory() as static_dir:
            with self.settings(
                STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
                STATIC_COMPRESS_MIN_SIZE_KB=1,
                STATIC_ROOT=self.temp_dir.name,
                STATICFILES_DIRS=[static_dir],
            ):
                output_file_path = self.temp_dir_path / "test.js"
                compressed_file_path = self.temp_dir_path / "test.js.gz"

                static_file = Path(static_dir) / "test.js"
                with static_file.open("wb") as fp:
                    fp.write(b"a" * 5000)

                call_command("collectstatic", interactive=False, verbosity=0)

                self.assertFileExist(output_file_path)
                self.assertFileExist(compressed_file_path)

                # Fake that the file has been written long ago
                os.utime(output_file_path, times=(1, 1))
                os.utime(compressed_file_path, times=(1, 1))

                expected_content = b"b" * 1023
                with static_file.open("wb") as fp:
                    fp.write(expected_content)

                call_command("collectstatic", interactive=False, verbosity=0)

                self.assertFileExist(output_file_path)
                self.assertEqual(output_file_path.read_bytes(), expected_content)
                self.assertFileNotExist(compressed_file_path)

    def test_post_process_storage_without_path(self):
        from static_compress.mixin import CompressMixin

        class PathlessCompressedStorage(CompressMixin, PathlessBaseStorage):
            pass

        class SourceStorage:
            def __init__(self, mtime):
                self._mtime = mtime

            def get_modified_time(self, name):
                return self._mtime

        with self.settings(
            STATIC_COMPRESS_MIN_SIZE_KB=1,
            STATIC_COMPRESS_METHODS=["gz+zlib"],
            STATIC_COMPRESS_FILE_EXTS=["js"],
        ):
            storage = PathlessCompressedStorage()
            storage._files["test.js"] = b"a" * 5000
            storage._mtimes["test.js"] = timezone.now()

            source_storage = SourceStorage(storage._mtimes["test.js"])
            paths = {"test.js": (source_storage, "test.js")}

            list(storage.post_process(paths, dry_run=False))

            self.assertTrue(storage.exists("test.js.gz"))

    def test_collectstatic_skips_when_compressed_newer(self):
        with tempfile.TemporaryDirectory() as static_dir:
            with self.settings(
                STORAGES={"staticfiles": {"BACKEND": "static_compress.storage.CompressedStaticFilesStorage"}},
                STATIC_COMPRESS_MIN_SIZE_KB=1,
                STATIC_COMPRESS_METHODS=["gz+zlib"],
                STATIC_ROOT=self.temp_dir.name,
                STATICFILES_DIRS=[static_dir],
            ):
                output_file_path = self.temp_dir_path / "test.js"
                compressed_file_path = self.temp_dir_path / "test.js.gz"

                static_file = Path(static_dir) / "test.js"
                with static_file.open("wb") as fp:
                    fp.write(b"a" * 5000)

                call_command("collectstatic", interactive=False, verbosity=0)

                self.assertFileExist(output_file_path)
                self.assertFileExist(compressed_file_path)

                # Make compressed file newer than original
                os.utime(static_file, times=(1, 1))
                os.utime(output_file_path, times=(1, 1))
                os.utime(compressed_file_path, times=(100, 100))

                compressed_mtime_before = compressed_file_path.stat().st_mtime

                call_command("collectstatic", interactive=False, verbosity=0)

                compressed_mtime_after = compressed_file_path.stat().st_mtime
                self.assertEqual(compressed_mtime_before, compressed_mtime_after)

    def test_delete_original_only_once(self):
        from static_compress.mixin import CompressMixin

        class CountingStorage(CompressMixin, FileSystemStorage):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.delete_calls = {}

            def delete(self, name):
                self.delete_calls[name] = self.delete_calls.get(name, 0) + 1
                return super().delete(name)

        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as dest_dir:
            with self.settings(
                STATIC_COMPRESS_MIN_SIZE_KB=1,
                STATIC_COMPRESS_METHODS=["gz+zlib", "br"],
                STATIC_COMPRESS_FILE_EXTS=["js"],
                STATIC_COMPRESS_KEEP_ORIGINAL=False,
            ):
                content = b"a" * 5000
                Path(src_dir, "test.js").write_bytes(content)
                Path(dest_dir, "test.js").write_bytes(content)

                storage = CountingStorage(location=dest_dir)
                source_storage = FileSystemStorage(location=src_dir)
                paths = {"test.js": (source_storage, "test.js")}

                list(storage.post_process(paths, dry_run=False))

                self.assertEqual(storage.delete_calls.get("test.js"), 1)




