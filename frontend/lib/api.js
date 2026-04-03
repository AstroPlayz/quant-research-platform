import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'

export async function runBacktest(payload) {
  const { data } = await axios.post(`${API_BASE_URL}/api/backtest`, payload)
  return data
}

export async function runGridSearch(payload) {
  const { data } = await axios.post(`${API_BASE_URL}/api/optimize/grid`, payload)
  return data
}

export async function runGenetic(payload) {
  const { data } = await axios.post(`${API_BASE_URL}/api/optimize/genetic`, payload)
  return data
}

export async function saveStrategy(name, payload) {
  const { data } = await axios.post(`${API_BASE_URL}/api/strategies/save`, { name, payload })
  return data
}

export async function listStrategies() {
  const { data } = await axios.get(`${API_BASE_URL}/api/strategies`)
  return data
}

export async function loadStrategy(name) {
  const { data } = await axios.get(`${API_BASE_URL}/api/strategies/${name}`)
  return data
}
