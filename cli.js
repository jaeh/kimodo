#!/usr/bin/env node

import { cli } from '@magic/cli'

const argv = cli({
  name: 'kimodo-cli',
  text: 'CLI tool for RunPod API requests',
  commands: [
    ['request', 'req'],
    ['status'],
  ],
  options: [
    ['--url', '-u'],
    ['--method', '-m'],
    ['--prompt', '-p'],
    ['--api-key', '-k'],
    ['--header', '-H'],
    ['--body', '-b'],
    ['--json', '-j'],
  ],
  default: {
    '--method': 'POST',
    '--url': 'https://api.runpod.ai/v2/qdgrecg73wvu6z/run',
  },
  single: ['--url', '--method', '--prompt', '--api-key', '--body'],
  required: ['--url'],
  help: {
    name: 'kimodo-cli',
    text: 'CLI tool for RunPod API requests',
    commands: {
      request: 'Make an API request (default)',
      status: 'Check request status',
    },
    options: {
      '--url': 'API endpoint URL',
      '--method': 'HTTP method (default: POST)',
      '--prompt': 'Prompt text for the request body',
      '--api-key': 'API key for authorization',
      '--header': 'Custom headers (format: "Key: Value")',
      '--body': 'Raw request body as JSON string',
      '--json': 'Parse response as JSON',
    },
  },
})

// Build headers
const headers = {
  'Content-Type': 'application/json',
}

if (argv.args.apiKey) {
  headers['Authorization'] = `Bearer ${argv.args.apiKey}`
}

if (argv.args.header) {
  const [key, ...valueParts] = argv.args.header.split(':')
  headers[key.trim()] = valueParts.join(':').trim()
}

// Build body
let body = {}

if (argv.args.prompt) {
  body = { input: { prompt: argv.args.prompt } }
}

if (argv.args.body) {
  try {
    body = JSON.parse(argv.args.body)
  } catch {
    console.error('Error: Invalid JSON in --body')
    process.exit(1)
  }
}

// Make the request
async function makeRequest() {
  const url = argv.args.url
  const method = argv.args.method || 'POST'

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    if (argv.args.json) {
      const data = await response.json()
      console.log(JSON.stringify(data, null, 2))
    } else {
      const text = await response.text()
      console.log(text)
    }

    return response
  } catch (error) {
    console.error('Error:', error.message)
    process.exit(1)
  }
}

// Check status
async function checkStatus() {
  const jobId = argv.args.url.split('/').pop()
  const statusUrl = `https://api.runpod.ai/v2/qdgrecg73wvu6z/status/${jobId}`

  try {
    const response = await fetch(statusUrl, {
      headers: {
        'Authorization': `Bearer ${argv.args.apiKey}`,
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log(JSON.stringify(data, null, 2))
  } catch (error) {
    console.error('Error:', error.message)
    process.exit(1)
  }
}

// Execute based on command
if (argv.commands.request) {
  makeRequest()
} else if (argv.commands.status) {
  checkStatus()
} else {
  // Default: make request
  makeRequest()
}
