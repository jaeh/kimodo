#!/bin/bash
# Kimodo startup script for RunPod
set -e

echo "🚀 Starting Kimodo Motion Generation"
echo "===================================="

# Check for HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo ""
    echo "❌ ERROR: HF_TOKEN is not set!"
    echo ""
    echo "You must provide a HuggingFace token with access to:"
    echo "  https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct"
    echo ""
    echo "Set it in RunPod's environment variables as a secret."
    echo ""
    exit 1
fi

# Login to HuggingFace
echo "📦 Logging into HuggingFace..."
python -c "from huggingface_hub import login; login('$HF_TOKEN')" || {
    echo "⚠️  Warning: Could not login to HuggingFace"
}

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "🖥️  GPU Info:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
    echo ""
    
    VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1 | tr -d ' ')
    if [ "$VRAM" -lt 17000 ]; then
        echo "⚠️  VRAM < 17GB detected."
        echo "   Text encoder will run on CPU (slower but works)."
        echo "   Set TEXT_ENCODER_DEVICE=cpu for better stability."
        echo ""
    fi
fi

# Check if Kimodo is installed
cd /workspace
if [ -d "kimodo" ]; then
    echo "✅ Kimodo found at /workspace/kimodo"
else
    echo "❌ Kimodo not found at /workspace/kimodo"
    echo "   Please ensure the container was built with the Dockerfile"
    exit 1
fi

# Create health check file
touch /workspace/.health_check

echo ""
echo "===================================="
echo "🎬 Starting Kimodo Demo"
echo "   URL: http://localhost:7860"
echo "===================================="
echo ""

# Start the demo
exec python -m kimodo.demo
