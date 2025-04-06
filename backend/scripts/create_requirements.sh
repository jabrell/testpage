#!/usr/bin/env bash

# Create requirements.txt file
uv export --no-hashes --format requirements-txt --all-groups > requirements_dev.txt
uv export --no-hashes --format requirements-txt > requirements.txt