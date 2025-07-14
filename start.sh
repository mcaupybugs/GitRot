#!/bin/bash
set -e

echo "🚀 Starting GitRot Application..."
echo "📡 FastAPI will be available on port 8000"
echo "🎨 Next.js will be available on port 3000"

export GIT_PYTHON_REFRESH=quiet
export GIT_PYTHON_GIT_EXECUTABLE=$(which git)

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
