#!/usr/bin/env bash

if [[ "${1}" = "run" ]]
then
    exec flask run --host=0.0.0.0 --port="${PORT}"
else
    exec "$@"
fi
