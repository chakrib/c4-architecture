#!/bin/bash
set -e

echo "Building Lambda Layer..."

# Navigate to the layers directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAYERS_DIR="$SCRIPT_DIR/../../layers"
COMMON_DIR="$LAYERS_DIR/common"

# Create temporary build directory
BUILD_DIR="$LAYERS_DIR/build"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/python"

echo "Installing Python dependencies..."
# Install for Linux x86_64 architecture (Lambda runtime)
# Only install pydantic (boto3/botocore are pre-installed in Lambda Python 3.11 runtime)
pip3 install pydantic==2.10.3 \
  -t "$BUILD_DIR/python" \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.11 \
  --only-binary=:all: \
  --upgrade \
  --no-cache-dir

# Copy common utilities
echo "Copying common utilities..."
cp -r "$COMMON_DIR/python/"* "$BUILD_DIR/python/"

# Remove unnecessary files to reduce size
echo "Cleaning up unnecessary files..."
cd "$BUILD_DIR/python"

# Remove test files and documentation
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove documentation files
find . -name "*.md" -delete 2>/dev/null || true
find . -name "*.txt" -delete 2>/dev/null || true
find . -name "*.rst" -delete 2>/dev/null || true

# Create zip file
echo "Creating layer zip file..."
cd "$BUILD_DIR"
zip -r "$LAYERS_DIR/common.zip" python/ -q

# Cleanup
cd "$LAYERS_DIR"
rm -rf "$BUILD_DIR"

echo "✓ Lambda layer built successfully: $LAYERS_DIR/common.zip"
echo "  Size: $(du -h "$LAYERS_DIR/common.zip" | cut -f1)"

# Check size
SIZE_BYTES=$(stat -f%z "$LAYERS_DIR/common.zip" 2>/dev/null || stat -c%s "$LAYERS_DIR/common.zip" 2>/dev/null)
MAX_SIZE=67108864  # 64MB (leaving buffer for 70MB limit)

if [ "$SIZE_BYTES" -gt "$MAX_SIZE" ]; then
  echo "⚠️  Warning: Layer size ($SIZE_BYTES bytes) exceeds recommended limit"
  echo "   Consider removing more unnecessary files"
else
  echo "✓ Layer size is within limits"
fi
