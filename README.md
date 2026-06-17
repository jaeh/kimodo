# Kimodo on RunPod

[NVIDIA's Kimodo](https://research.nvidia.com/labs/sil/projects/kimodo/): Fast Text-to-Motion Generation from text descriptions.

## ⚠️ Important Prerequisites

### 1. HuggingFace Access (Required)

1. **Request access** to [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
2. **Create an access token** at https://huggingface.co/settings/tokens (need "read" type)

### 2. Hardware Requirements

| VRAM  | Mode             | Notes                               |
| ----- | ---------------- | ----------------------------------- |
| ≥17GB | Full GPU         | Fast inference (~10-30s per motion) |
| <16GB | CPU text encoder | Slower but works                    |

**Recommended GPUs**: RTX 3090, RTX 4090, A100

## 🚀 Quick Start on RunPod

### Option A: Custom Container (Recommended)

1. **Build the Docker image** locally first:

   ```bash
   docker build -t kimodo .
   ```

2. **Push to a container registry** (Docker Hub, GHCR, etc.)

3. **Deploy on RunPod**:
   - Use "Custom Container" template
   - Set `HF_TOKEN` as a secret environment variable
   - Set container start command: `bash /workspace/start.sh`
   - GPU: RTX 4090 24GB or A100

### Option B: Template (if available)

Search for "Kimodo" in RunPod community templates.

## 📁 Files Included

| File                 | Purpose                       |
| -------------------- | ----------------------------- |
| `Dockerfile`         | Container image definition    |
| `runpod.toml`        | RunPod deployment config      |
| `start.sh`           | Auto-install & startup script |
| `docker-compose.yml` | Local multi-service setup     |
| `.env.example`       | Environment template          |

## 🖥️ Accessing the Demo

After deployment:

- **Demo UI**: `http://<your-server-ip>:7860`
- **Interactive**: Generate motions via web interface
- **Constraints**: Add spatial/temporal constraints in the UI

## 💻 Server CLI

SSH into your pod and run:

### Kimodo Server Commands

```bash
# Basic motion generation
kimodo_gen "A person walks forward." \
    --model Kimodo-SOMA-RP-v1 \
    --duration 5.0 \
    --output output

# With CPU text encoder (for <16GB VRAM)
TEXT_ENCODER_DEVICE=cpu kimodo_gen "A person runs." --model Kimodo-SOMA-RP-v1

# List available models
kimodo_gen --help
```

### RunPod API CLI

After deploying, you can also interact with the RunPod API directly using the Node.js CLI:

```bash
# Install globally (or use npm link in project)
npm link

# Basic API request
kimodo -k YOUR_API_KEY -p "A person walks forward"

# Or set RUNPOD_API_KEY in a .env file (no -k flag needed)
echo "RUNPOD_API_KEY=your_key_here" > .env
kimodo -p "A person walks forward"

# With custom endpoint and body
kimodo -u https://api.runpod.ai/v2/your-endpoint/run \
       -k YOUR_API_KEY \
       -b '{"input":{"prompt":"A person waves"}}'

# Check job status
kimodo status -k YOUR_API_KEY -u https://api.runpod.ai/v2/your-endpoint/status/JOB_ID

# Show help
kimodo --help
```

**CLI Options:**

| Flag        | Alias | Description                          |
| ----------- | ----- | ------------------------------------ |
| `--url`     | `-u`  | API endpoint URL                     |
| `--method`  | `-m`  | HTTP method (default: POST)          |
| `--prompt`  | `-p`  | Prompt text for request body         |
| `--api-key` | `-k`  | API key for authorization            |
| `--header`  | `-H`  | Custom headers ("Key: Value")        |
| `--body`    | `-b`  | Raw request body as JSON string      |
| `--json`    | `-j`  | Parse and pretty-print response JSON |

## 📦 Available Models

| Model                 | Dataset                    | Skeleton | Quality     |
| --------------------- | -------------------------- | -------- | ----------- |
| `Kimodo-SOMA-RP-v1`   | Full Bones Rigplay (700hr) | SOMA     | ⭐⭐⭐ Best |
| `Kimodo-G1-RP-v1`     | Full Bones Rigplay (700hr) | G1       | ⭐⭐⭐ Best |
| `Kimodo-SOMA-Seed-v1` | BONES-SEED (288hr)         | SOMA     | ⭐⭐ Good   |
| `Kimodo-G1-Seed-v1`   | BONES-SEED (288hr)         | G1       | ⭐⭐ Good   |

## 🔧 Troubleshooting

### "Model not found" errors

- Ensure `HF_TOKEN` is set and valid
- First run downloads models (~5-10GB)

### Out of Memory (OOM)

- Set `TEXT_ENCODER_DEVICE=cpu`
- Reduce generation duration

### Slow inference

- Normal on first run (model loading)
- Use GPU mode for best performance

## 📚 API Usage

```python
from kimodo import KimodoModel

# Load model
model = KimodoModel("Kimodo-SOMA-RP-v1")

# Generate motion
motion = model.generate(
    prompt="A person waves hello",
    duration=3.0,
)

# Save in various formats
motion.save("output.bvh")  # BVH
motion.save("output.fbx")  # FBX
motion.save("output.npz") # NumPy
motion.save("output.glb")  # GLB/GLTF
```

## 📄 License

Kimodo is research code under a custom license. See [NVIDIA's license terms](https://github.com/nv-tlabs/kimodo/blob/main/LICENSE).
