#!/usr/bin/env bash
set -euo pipefail

# NFR-001 metric 2: dependency installation happens before this verifier.
# Each measured command runs in its own network namespace, and failure to
# establish isolation stops the gate before either command is launched.
unshare --net /bin/true
unshare --net make schemas-check
unshare --net make test
