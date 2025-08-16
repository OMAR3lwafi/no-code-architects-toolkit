#!/bin/bash

# Prepare Lambda deployment with optimized requirements
# This script sets up the Lambda-optimized dependencies

set -e

echo "🔧 Preparing Lambda deployment..."

# Backup original requirements
if [ ! -f "requirements-original.txt" ]; then
    echo "📦 Backing up original requirements..."
    cp requirements.txt requirements-original.txt
fi

# Use Lambda-optimized requirements
echo "⚡ Using Lambda-optimized requirements..."
cp requirements-lambda.txt requirements.txt

echo "🎯 Lambda preparation complete!"
echo ""
echo "⚠️  Note: Heavy dependencies (torch, whisper, matplotlib) excluded"
echo "💡 For ML features, consider using Lambda container images or separate functions"
echo ""
echo "Next steps:"
echo "1. sam build"
echo "2. sam deploy --guided"
echo "3. After deployment, restore original requirements: cp requirements-original.txt requirements.txt"