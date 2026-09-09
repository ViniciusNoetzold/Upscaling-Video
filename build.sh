#!/usr/bin/env bash
set -o errexit

echo "==> [Mezzold Studio] Building Upscaling-Video..."
pip install --upgrade pip
pip install -r requirements.txt
echo "==> Build complete!"
