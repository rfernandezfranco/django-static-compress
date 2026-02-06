# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
- Fall back to original file metadata when `STATIC_COMPRESS_KEEP_ORIGINAL=False` and compressed variants are skipped by `STATIC_COMPRESS_MIN_SIZE_KB`.
- Use storage compatibility fallback for compressed-file existence checks in `post_process`, avoiding failures when storage backends do not implement `exists()`.

### Changed
- Tests: Add coverage for metadata fallback to original files and compressed-variant precedence for metadata lookups.
- Tests: Add coverage for `post_process` compatibility with storages that rely on `path()` fallback when `exists()` is not implemented.

## [3.0.1] - 2026-02-06
### Changed
- Migrate development linting from Pylint to Ruff, drop `pylintrc`, and centralize Ruff settings in `pyproject.toml`.
- Modernize pre-commit and development workflow documentation (current hook versions, no legacy Prettier hook, and updated setup/test commands).

## [3.0.0] - 2026-02-06
### Fixed
- Fix manifest path selection for compressed files by preferring `hashed_files` mappings and falling back to `hashed_name` or original paths when needed.

### Changed
- Align minimum Django version with supported Python range.
- Bump Python support metadata to 3.10+.
- Clarify that `STATIC_COMPRESS_MIN_SIZE_KB` takes precedence over `STATIC_COMPRESS_KEEP_ORIGINAL` for small files.
- Tests: Add coverage to ensure small files keep originals and skip compressed variants when `KEEP_ORIGINAL=False`.
- Refactor storage access to prefer storage APIs (`exists`, `size`, and time lookups) with `path()` fallback, and improve errors when neither interface is available.
- Use storage-backed compressed name/time resolution when originals are removed to improve compatibility with non-filesystem storages.
- Tests: Add coverage for `post_process` behavior with storages that do not implement `path()`.
- Add a pre-check pass to determine which compressed variants need updates before opening source files.
- Tests: Add coverage to ensure recompression is skipped when compressed files are newer than originals.
- Tests: Make manifest integration tests hash-agnostic by reading hashed filenames from `staticfiles.json` instead of hardcoded digests.
- Update Travis CI to test Python 3.10-3.14 (3.14 as allow-failure), use editable install via pip, and replace `setup.py test` with unittest discovery.
- Delete original files only once per asset and only after compressed variants are saved.
- Tests: Add coverage for delete-once behavior when multiple compressors are enabled.

### Security
- Raise minimum Brotli and Zopfli versions (Brotli>=1.2.0, zopfli>=0.3.0).

## [2.1.0] - 2025-02-21
### Fixed
- Remove compressed files if one exists, but the original files is under `STATIC_COMPRESS_MIN_SIZE_KB`. (#211, thanks @Stegopoelkus)

## [2.0.0] - 2021-05-20
### Removed
- Remove `CompressedCachedStaticFilesStorage` as Django has removed it

## [1.2.1] - 2018-08-02
### Fixed
- Updated static's compressed file are now properly updated (#7, #8, thanks @hongquan)

## [1.2.0] - 2018-07-30
### Added
- Added the following settings (#2, thanks @hongquan)
  - `STATIC_COMPRESS_FILE_EXTS`
  - `STATIC_COMPRESS_METHODS`
  - `STATIC_COMPRESS_KEEP_ORIGINAL`
- Added method `gz+zlib` for gzip compression without Zopfli

### Changed
- Files smaller than 30kB are no longer compressed. This is the value that Webpack base on to split chunks
  - Set `STATIC_COMPRESS_MIN_SIZE_KB=0` to restore original behavior
- Added coding standard checkers and formatters

## [1.1.1] - 2017-12-24
### Changed
- Updated Brotli and Zopfli

[unreleased]: https://github.com/rfernandezfranco/django-static-compress/compare/v3.0.1...HEAD
[3.0.1]: https://github.com/rfernandezfranco/django-static-compress/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/rfernandezfranco/django-static-compress/compare/v2.1.0...v3.0.0
[2.1.0]: https://github.com/whs/django-static-compress/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/whs/django-static-compress/compare/v1.2.1...v2.0.0
[1.2.1]: https://github.com/whs/django-static-compress/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/whs/django-static-compress/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/whs/django-static-compress/compare/v1.1.0...v1.1.1
