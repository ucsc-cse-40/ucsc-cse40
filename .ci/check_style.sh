#!/bin/bash

# Check all .py and .ipynb files in this project for style.

readonly THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly BASE_DIR=$(realpath "${THIS_DIR}/..")

function main() {
    if [[ $# -ne 0 ]]; then
        echo "USAGE: $0"
        exit 1
    fi

    trap exit SIGINT

    local error_count=0
    for path in $(find "${BASE_DIR}" \( -name '*.py' -o -name '*.ipynb' \)) ; do
        if [[ "${path}" == *'.ipynb_checkpoints'* ]] ; then
            continue
        fi

        echo "Checking ${path}."
        python3 -m cse40.style "${path}"
        ((error_count += $?))
    done

    if [[ ${error_count} -gt 0 ]] ; then
        echo "Found ${error_count} style issues."
    else
        echo "No style issues found."
    fi

    return ${error_count}
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
