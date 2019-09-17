#!/bin/bash

CSFILES="*.cs"
CSPROJ="*.csproj"

print_usage () {
    echo "usage: namespacefix /path/to/project"
    echo "/path/to/project should contain csproj file at least"
    exit 1
}

if [[ $# -lt 1 || ! -d $1 || ! -n "$(ls -A $1/$CSPROJ 2>/dev/null)" ]] ; then
    print_usage
fi

ABS_PATH="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
PROJ_ROOT=$(basename $1)

find "$ABS_PATH" -type f -name "$CSFILES" ! -path "*/obj/*" -print0 |
    while IFS= read -r -d '' file; do
        actual_ns=$(sed -n 's/^namespace\s\(.*\)/\1/p' "$file" | tr -d ' ')
        expected_ns=$(echo "$(dirname "$file")" | grep -o "\b$PROJ_ROOT\b.*" | tr '/' '.')
        if [ "$actual_ns" != "$expected_ns" ]
        then
            echo "$file is inconsistent!"
            echo "expected: $expected_ns"
            echo "actual: $actual_ns"
            sed -i "s/^namespace\s.*/namespace $expected_ns/" "$file" && echo "edited in-place"
        fi
    done
