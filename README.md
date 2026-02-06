# Django-static-compress

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Precompress your static files automatically with [Brotli](https://github.com/google/brotli) and [Zopfli](https://github.com/obp/zopfli)

## Project status

This fork is actively maintained to continue the original project.

- Fork repository: [rfernandezfranco/django-static-compress](https://github.com/rfernandezfranco/django-static-compress)
- Original project: [whs/django-static-compress](https://github.com/whs/django-static-compress)

## Installation

Install this from pip:

```sh
$ pip install django-static-compress
```

(you may want to write this in your requirements.txt)

Then update your settings.py:

```py
STORAGES = {
    "staticfiles": {
        "BACKEND": "static_compress.storage.CompressedStaticFilesStorage",
    },
}
```

When you run `python manage.py collectstatic` it will have an additional post-processing pass to compress your static files.

Make sure that your web server is configured to serve precompressed static files:

- If using nginx:
  - Setup [ngx_http_gzip_static_module](https://nginx.org/en/docs/http/ngx_http_gzip_static_module.html) to serve gzip (.gz) precompressed files.
  - Out of tree module [ngx_brotli](https://github.com/google/ngx_brotli) is required to serve Brotli (.br) precompressed files.
- [Caddy](https://caddyserver.com) will serve .gz and .br without additional configuration.

Also, as Brotli is not supported by all browsers you should make sure that your reverse proxy/CDN honor the Vary header, and your web server set it to [`Vary: Accept-Encoding`](https://blog.stackpath.com/accept-encoding-vary-important).

## Available storages

- `static_compress.CompressedStaticFilesStorage`: Generate `.br` and `.gz` from your static files
- `static_compress.CompressedManifestStaticFilesStorage`: Like [`ManifestStaticFilesStorage`](https://docs.djangoproject.com/en/1.11/ref/contrib/staticfiles/#manifeststaticfilesstorage), but also generate compressed files for the hashed files

You can also add support to your own backend by applying `static_compress.CompressMixin` to your class.

By default it will only compress files ending with `.js`, `.css` and `.svg`. This is controlled by the settings below.

## Settings

_django-static-compress_ settings and their default values:

```py
STATIC_COMPRESS_FILE_EXTS = ['js', 'css', 'svg']
STATIC_COMPRESS_METHODS = ['gz', 'br']
STATIC_COMPRESS_KEEP_ORIGINAL = True
STATIC_COMPRESS_MIN_SIZE_KB = 30
```

After compressing the static files, _django-static-compress_ still leaves the original files in _STATIC_ROOT_ folder. If you want to delete (to save disk space), change `STATIC_COMPRESS_KEEP_ORIGINAL` to `False`.

If the file is too small, it isn't worth compressing. You can change the minimum size in KiB at which file should be compressed, by changing `STATIC_COMPRESS_MIN_SIZE_KB`.

**Interaction between `STATIC_COMPRESS_MIN_SIZE_KB` and `STATIC_COMPRESS_KEEP_ORIGINAL`:**

If a file is smaller than `STATIC_COMPRESS_MIN_SIZE_KB`, compressed variants are removed (or not generated). In this case, the original file is **always kept**, even if `STATIC_COMPRESS_KEEP_ORIGINAL=False`. This avoids serving stale compressed files and prevents losing the asset entirely when it is too small to compress.

By default, _django-static-compress_ use Zopfli to compress to gzip. Zopfli compress better than gzip, but will take more time to compress. If you want to create gzip file with built-in zlib compressor, replace `'gz'` with `'gz+zlib'` in `STATIC_COMPRESS_METHODS`.

## File size reduction

Here's some statistics from [TipMe](https://tipme.in.th)'s jQuery and React bundle. Both bundle have related plugins built in with webpack (eg. Bootstrap for jQuery bundle, and [classnames](https://github.com/JedWatson/classnames) for React bundle), and is already minified.

```
101K jquery.9aa33728c6b5.js
 33K jquery.9aa33728c6b5.js.gz (33%)
 31K jquery.9aa33728c6b5.js.br (31%)
174K react.5c4899aeda53.js
 51K react.5c4899aeda53.js.gz (29%)
 44K react.5c4899aeda53.js.br (25%)
```

(.gz is Zopfli compressed, and .br is Brotli compressed)

## Development

This fork is actively maintained. Issues and pull requests are welcome.

Development workflow:

1.  Run `pip install -e .`
2.  Run `pip install -r requirements-dev.txt && pre-commit install`
3.  Start hacking
4.  Run test: `python -m unittest discover -s test`
5.  Run integration test: `cd integration_test; python manage.py test`
6.  Run hooks manually when needed: `pre-commit run --all-files`
7.  Commit. Pre-commit will warn if you have any changes.

Lint policy:

- Local development uses autofix-capable pre-commit hooks.
- CI runs check-only lint/format validation in `.github/workflows/lint.yml`.

Process conventions:

- See `AGENTS.md` for planning, commit, changelog, and release conventions used in this repository.

## License

Licensed under the [MIT License](LICENSE)
