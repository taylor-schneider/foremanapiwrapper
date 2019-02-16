#!/bin/bash

set -e

VERSION=$(python --version 2>&1 | sed -e "s/^Python //" | cut -c1)
PIP="pip"
PACKAGES="install"

if [ "$VERSION" -lt 3 ]; then
    PACKAGES="$PACKAGES future"
fi

$PIP install requests future