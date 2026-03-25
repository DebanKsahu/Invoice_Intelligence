# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- None.

### Changed
- None.

### Fixed
- None.

### Removed
- None.

## [0.3.2] - 2026-03-25

### Added
- None.

### Changed
- None.

### Fixed
- Fixed Gmail webhook user email detail assignment in `handleGmailWebhook`.

### Removed
- None.

## [0.3.1] - 2026-03-25

### Added
- None.

### Changed
- None.

### Fixed
- Fixed Gmail webhook duplicate Pub/Sub processing by persisting `historyId` before async processing.

### Removed
- None.

## [0.3.0] - 2026-03-24

### Added
- Added Excel sheet generation for invoice output.

### Changed
- Updated project version to `0.3.0`.
- Added and expanded changelog tracking for release documentation.

### Fixed
- None.

### Removed
- None.

## [0.2.0] - 2026-03-21

### Added
- Added PostgreSQL initialization during application lifespan setup.
- Added Gmail webhook support for invoice processing, including new message history tracking and stale event filtering.
- Added invoice and PDF domain models for extraction, validation, and page-level summaries.
- Added Gmail attachment and message models to support webhook processing flows.
- Added Google OAuth enhancements including code verifier flow and additional authentication scopes.

### Changed
- Changed application startup structure by moving dependency setup into a dedicated function.
- Changed Docker configuration to simplify container setup and correct exposed port behavior.
- Changed Gmail webhook orchestration to improve user creation and update behavior with observer metadata.
- Changed project documentation for clearer setup, usage, and AI extraction details.

### Fixed
- Fixed Gmail webhook history list request execution.
- Fixed auth callback handling for HTTP error scenarios.
- Fixed auth callback session handling logic.
- Fixed settings environment file assignment.
- Fixed database model handling by allowing `None` for `gmailObserverExpiry`.

### Removed
- Removed logger parameter from Gmail webhook handler entrypoint.

[Unreleased]: https://github.com/DebanKsahu/Invoice_Intelligence/compare/v0.3.2...HEAD
[0.3.2]: https://github.com/DebanKsahu/Invoice_Intelligence/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/DebanKsahu/Invoice_Intelligence/releases/tag/v0.3.1
[0.3.0]: https://github.com/DebanKsahu/Invoice_Intelligence/releases/tag/v0.3.0
[0.2.0]: https://github.com/DebanKsahu/Invoice_Intelligence/releases/tag/v0.2.0
