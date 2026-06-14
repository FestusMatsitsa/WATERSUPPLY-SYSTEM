#!/bin/bash
set -e
cd /home/runner/workspace/artifacts/aqualife-django
python3.11 manage.py migrate --run-syncdb 2>/dev/null || true
exec python3.11 manage.py runserver 0.0.0.0:${PORT:-8000} --noreload
