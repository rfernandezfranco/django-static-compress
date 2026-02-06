import errno
import os
from os.path import getatime, getctime, getmtime

from django.core.exceptions import ImproperlyConfigured

from . import compressors

__all__ = ["CompressMixin"]


DEFAULT_METHODS = ["gz", "br"]
METHOD_MAPPING = {
    "gz": compressors.ZopfliCompressor,
    "br": compressors.BrotliCompressor,
    "gz+zlib": compressors.ZlibCompressor,
    # gz+zlib and gz cannot be used at the same time, because they produce the same file extension.
}


class CompressMixin:
    allowed_extensions = []
    compress_methods = []
    keep_original = True
    compressors = []
    minimum_kb = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We access Django settings lately here, to allow our app to be imported without
        # defining DJANGO_SETTINGS_MODULE.
        from django.conf import settings

        self.allowed_extensions = getattr(settings, "STATIC_COMPRESS_FILE_EXTS", ["js", "css", "svg"])
        self.compress_methods = getattr(settings, "STATIC_COMPRESS_METHODS", DEFAULT_METHODS)
        self.keep_original = getattr(settings, "STATIC_COMPRESS_KEEP_ORIGINAL", True)
        self.minimum_kb = getattr(settings, "STATIC_COMPRESS_MIN_SIZE_KB", 30)

        valid = [i for i in self.compress_methods if i in METHOD_MAPPING]
        if not valid:
            raise ImproperlyConfigured("No valid method is defined in STATIC_COMPRESS_METHODS setting.")
        if "gz" in valid and "gz+zlib" in valid:
            raise ImproperlyConfigured("STATIC_COMPRESS_METHODS: gz and gz+zlib cannot be used at the same time.")
        self.compressors = [METHOD_MAPPING[k]() for k in valid]

    def _try_path(self, name):
        try:
            return self.path(name)
        except (AttributeError, NotImplementedError):
            return None

    def _storage_exists(self, name):
        try:
            return self.exists(name)
        except (AttributeError, NotImplementedError) as exc:
            path = self._try_path(name)
            if path is None:
                raise ImproperlyConfigured(f"Storage must implement exists() or provide path() for {name}") from exc
            return os.path.exists(path)

    def _storage_size(self, name):
        try:
            return self.size(name)
        except (AttributeError, NotImplementedError) as exc:
            path = self._try_path(name)
            if path is None:
                raise ImproperlyConfigured(f"Storage must implement size() or provide path() for {name}") from exc
            return os.path.getsize(path)

    def _storage_get_accessed_time(self, name):
        try:
            return super().get_accessed_time(name)
        except (AttributeError, NotImplementedError) as exc:
            path = self._try_path(name)
            if path is None:
                raise ImproperlyConfigured(
                    f"Storage must implement get_accessed_time() or provide path() for {name}"
                ) from exc
            return self._datetime_from_timestamp(getatime(path))

    def _storage_get_created_time(self, name):
        try:
            return super().get_created_time(name)
        except (AttributeError, NotImplementedError) as exc:
            path = self._try_path(name)
            if path is None:
                raise ImproperlyConfigured(
                    f"Storage must implement get_created_time() or provide path() for {name}"
                ) from exc
            return self._datetime_from_timestamp(getctime(path))

    def _storage_get_modified_time(self, name):
        try:
            return super().get_modified_time(name)
        except (AttributeError, NotImplementedError) as exc:
            path = self._try_path(name)
            if path is None:
                raise ImproperlyConfigured(
                    f"Storage must implement get_modified_time() or provide path() for {name}"
                ) from exc
            return self._datetime_from_timestamp(getmtime(path))

    def get_alternate_compressed_name(self, name):
        for compressor in self.compressors:
            ext = compressor.extension
            if name.endswith(f".{ext}"):
                candidate = name
            else:
                candidate = f"{name}.{ext}"
            if self._storage_exists(candidate):
                return candidate
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), name)

    def _get_metadata_target_name(self, name):
        if self.keep_original:
            return name
        try:
            return self.get_alternate_compressed_name(name)
        except FileNotFoundError:
            if self._storage_exists(name):
                return name
            raise

    def get_accessed_time(self, name):
        if self.keep_original:
            return super().get_accessed_time(name)
        return self._storage_get_accessed_time(self._get_metadata_target_name(name))

    def get_created_time(self, name):
        if self.keep_original:
            return super().get_created_time(name)
        return self._storage_get_created_time(self._get_metadata_target_name(name))

    def get_modified_time(self, name):
        if self.keep_original:
            return super().get_modified_time(name)
        return self._storage_get_modified_time(self._get_metadata_target_name(name))

    def post_process(self, paths, dry_run=False, **options):
        if hasattr(super(), "post_process"):
            yield from super().post_process(paths, dry_run, **options)

        if dry_run:
            return

        for name in paths.keys():
            if not self._is_file_allowed(name):
                continue

            source_storage, path = paths[name]
            dest_path = self._get_dest_path(path)
            # Process if file is big enough
            if self._storage_size(dest_path) < self.minimum_kb * 1024:
                # Delete old gzip file, or Nginx will pick the old file to serve.
                # Note: We have to delete the file in case it was created in a previous iteration.
                for compressor in self.compressors:
                    dest_compressor_path = f"{dest_path}.{compressor.extension}"
                    if self._storage_exists(dest_compressor_path):
                        self.delete(dest_compressor_path)
                continue
            src_mtime = source_storage.get_modified_time(path)
            to_compress = []
            for compressor in self.compressors:
                dest_compressor_path = f"{dest_path}.{compressor.extension}"
                if not self._storage_exists(dest_compressor_path):
                    to_compress.append((compressor, dest_compressor_path))
                    continue

                # Check if the original file has been changed.
                # If not, no need to compress again.
                try:
                    dest_mtime = self._storage_get_modified_time(dest_compressor_path)
                    file_is_unmodified = dest_mtime.replace(microsecond=0) >= src_mtime.replace(microsecond=0)
                except (FileNotFoundError, KeyError):
                    file_is_unmodified = False
                if not file_is_unmodified:
                    to_compress.append((compressor, dest_compressor_path))
            if not to_compress:
                continue
            with self._open(dest_path) as file:
                saved_any = False
                for compressor, dest_compressor_path in to_compress:
                    # Delete old gzip file, or Nginx will pick the old file to serve.
                    # Note: Django won't overwrite the file, so we have to delete it ourselves.
                    if self._storage_exists(dest_compressor_path):
                        self.delete(dest_compressor_path)
                    out = compressor.compress(path, file)

                    if out:
                        self._save(dest_compressor_path, out)
                        saved_any = True
                        yield dest_path, dest_compressor_path, True

                    file.seek(0)
            if saved_any and not self.keep_original:
                self.delete(name)

    def _get_dest_path(self, path):
        if hasattr(self, "hashed_files"):
            return self.hashed_files.get(path, path)
        if hasattr(self, "hashed_name"):
            return self.hashed_name(path)

        return path

    def _is_file_allowed(self, file):
        for extension in self.allowed_extensions:
            if file.endswith("." + extension):
                return True
        return False
