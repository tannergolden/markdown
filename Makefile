# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
#
# The kit is standard-library Python, so every target below runs on a bare
# `python3` (3.10 or later) with nothing installed.

PYTHON ?= python3
KIT    := $(PYTHON) src/markdown-kit.py
# Discovery from the repository's root, so every test imports `tests.support` the same way.
TEST   := $(PYTHON) -m unittest discover -t .

.DEFAULT_GOAL := help
.PHONY: help lint draw themes test test-unit test-integration test-e2e test-scripts holidays catalogue calibrate calibrated

## help: List the available targets
help:
	@echo "Markdown - the Markdown Kit"
	@echo
	@sed -n 's/^## //p' $(MAKEFILE_LIST) | awk -F': ' '{ printf "  %-18s %s\n", $$1, substr($$0, length($$1) + 3) }'

## lint: The repository's configuration parses, every module compiles, the layers import only what they may, and every design lints
lint:
	@$(PYTHON) .github/scripts/validate-repository.py
	@$(PYTHON) -m compileall -q src tests
	@$(TEST) -s tests/unit -p 'test_layering.py'
	@$(KIT) lint --specimen tests/fixtures/driftmark > /dev/null || $(KIT) lint --specimen tests/fixtures/driftmark

## draw: Draw a sample page into preview/ the way a run would, in the default theme (no network)
draw:
	@for mode in repository profile; do \
		rm -rf preview/$$mode && mkdir -p preview/$$mode/.github && \
		cp tests/fixtures/sample/markdown.yaml preview/$$mode/.github/markdown.yaml && \
		$(KIT) preview --root preview/$$mode --input mode=$$mode --today 2026-09-25 || exit 1; \
	done

## themes: Draw every theme into docs/themes, the page the README links to (no network)
themes:
	@$(PYTHON) .github/scripts/build-theme-sets.py docs/themes

## test: Everything CI runs: the kit's three suites and the repository script tests
test: test-unit test-integration test-e2e test-scripts

## test-unit: The rules, each in isolation (no git, no network), a module to a core at once
test-unit:
	@$(PYTHON) tests/parallel.py tests/unit 'test_*.py'

## test-integration: Git, files, the clock and the kit's data, on real temporary repositories
test-integration:
	@$(TEST) -s tests/integration -p 'test_*.py'

## test-e2e: The command line, run as a person runs it
test-e2e:
	@$(TEST) -s tests/e2e -p 'test_*.py'

## test-scripts: The repository's own scripts under .github/scripts
test-scripts:
	@$(PYTHON) -m unittest discover -s .github/scripts -p 'test_*.py'

## holidays: The holiday calendar for this year, at the default three days
holidays:
	@$(KIT) holidays --year $$(date -u +%Y)

## catalogue: Write docs/Catalogue.md from the trophies' catalogue and calibration
catalogue:
	@$(KIT) catalogue > docs/Catalogue.md

## calibrate: Measure the repository population through the API (needs GITHUB_TOKEN), then write what reads it
calibrate:
	@$(KIT) calibrate
	@$(MAKE) --no-print-directory calibrated

## calibrated: Write the catalogue again from the calibration on disk
calibrated: catalogue
