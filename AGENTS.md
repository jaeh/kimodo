# Agent Instructions for Kimodo CLI

This project includes a Node.js CLI (`cli.js`) for making RunPod API requests.

## Quick Reference

```bash
# Basic request with prompt
node cli.js -k YOUR_API_KEY -p "A person walks forward"

# Check job status
node cli.js status -k YOUR_API_KEY -u https://api.runpod.ai/v2/endpoint/status/JOB_ID

# With custom JSON body
node cli.js -k YOUR_API_KEY -b '{"input":{"prompt":"A person waves","duration":3.0}}'
```

## Options

| Flag        | Alias | Description                           |
| ----------- | ----- | ------------------------------------- |
| `--url`     | `-u`  | API endpoint URL                      |
| `--method`  | `-m`  | HTTP method (default: POST)           |
| `--prompt`  | `-p`  | Prompt text for request body          |
| `--api-key` | `-k`  | API key for authorization             |
| `--header`  | `-H`  | Custom headers (format: "Key: Value") |
| `--body`    | `-b`  | Raw request body as JSON string       |
| `--json`    | `-j`  | Parse response as JSON                |

## Environment Variable

If a `.env` file exists with `RUNPOD_API_KEY=xxx`, the CLI will read it automatically—no `-k` flag needed.

## Making a Motion Generation Request

```bash
node cli.js \
  -u https://api.runpod.ai/v2/qdgrecg73wvu6z/run \
  -k $RUNPOD_API_KEY \
  -p "A person raises their right arm"
```

## Checking Request Status

```bash
JOB_ID="abc123"
node cli.js status \
  -u https://api.runpod.ai/v2/qdgrecg73wvu6z/status/$JOB_ID \
  -k $RUNPOD_API_KEY
```
