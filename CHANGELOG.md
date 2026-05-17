# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-17

### Added

- `mask_text` MCP tool: masks PII in text using kuronuri with support for `en`/`ja` languages and `block`/`label`/`fixed` strategies
- `list_ner_tags` MCP tool: returns available NER tags for a given language model as a Markdown table
- pytest unit tests for `mask_text` and `list_ner_tags` with 100% coverage
- `mise.toml` with `fix`, `test`, and `test-all` tasks
- `ruff` and `ty` static analysis configuration in `pyproject.toml`
- Apache-2.0 license

[Unreleased]: https://github.com/shogo-ogami/kuronuri-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/shogo-ogami/kuronuri-mcp/releases/tag/v0.1.0
