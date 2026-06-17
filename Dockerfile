# Kimodo Dockerfile for RunPod
# Using NVIDIA's official PyTorch container

FROM nvcr.io/nvidia/pytorch:24.10-py3

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/workspace/.cache/huggingface

WORKDIR /workspace

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Remove broken cmake shim (shadows system cmake, breaks MotionCorrection C++ build)
RUN rm -f /usr/local/bin/cmake || true

# Clone Kimodo repo
RUN git clone https://github.com/nv-tlabs/kimodo.git /workspace/kimodo && \
    cd /workspace/kimodo && \
    git submodule update --init --recursive

WORKDIR /workspace/kimodo

# Clone kimodo-viser fork
RUN git clone https://github.com/nv-tlabs/kimodo-viser.git

# Install Kimodo:
# - Editable install (-e .) for kimodo package + CLI scripts (kimodo_gen, kimodo_demo, kimodo_textencoder)
# - SKIP_MOTION_CORRECTION_IN_SETUP=1 prevents setup.py from bundling MotionCorrection
# - MotionCorrection installed separately (non-editable, includes C++ compilation)
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip && \
    SKIP_MOTION_CORRECTION_IN_SETUP=1 python -m pip install -e . && \
    python -m pip install -e kimodo-viser && \
    python -m pip install ./MotionCorrection

# Copy and setup entrypoint script
COPY <<'EOF' /usr/local/bin/docker-entrypoint
#!/usr/bin/env bash
set -euo pipefail

HOST_UID="${HOST_UID:-}"
HOST_GID="${HOST_GID:-}"
HOST_USER="${HOST_USER:-user}"

if [[ -z "${HOST_UID}" || -z "${HOST_GID}" ]]; then
  if [[ -d /workspace ]]; then
    HOST_UID="$(stat -c %u /workspace)"
    HOST_GID="$(stat -c %g /workspace)"
  else
    HOST_UID="${HOST_UID:-1000}"
    HOST_GID="${HOST_GID:-1000}"
  fi
fi

if ! getent group "${HOST_GID}" >/dev/null 2>&1; then
  groupadd -g "${HOST_GID}" "${HOST_USER}"
fi

if ! getent passwd "${HOST_UID}" >/dev/null 2>&1; then
  useradd -m -u "${HOST_UID}" -g "${HOST_GID}" -s /bin/bash "${HOST_USER}"
fi

exec gosu "${HOST_UID}:${HOST_GID}" "$@"
EOF
chmod +x /usr/local/bin/docker-entrypoint

# Environment
ENV HF_TOKEN=""
ENV TEXT_ENCODER_DEVICE=cuda

EXPOSE 7860 9550

ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
CMD ["bash"]
