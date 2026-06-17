async function main() {
  const url = 'https://api.runpod.ai/v2/qdgrecg73wvu6z/run'

  const requestConfig = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer YOUR_API_KEY',
    },
    body: JSON.stringify({ input: { prompt: 'Your prompt' } }),
  }

  try {
    const response = await fetch(url, requestConfig)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log(data)
    return data
  } catch (error) {
    console.error('Error:', error)
    throw error
  }
}

// Execute the function
main()
  .then(result => console.log('Success:', result))
  .catch(error => console.error('Error:', error))
