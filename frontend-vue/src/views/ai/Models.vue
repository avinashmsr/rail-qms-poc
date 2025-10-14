<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { paths } from '@/api'

const info = ref<any>(null)
const metrics = ref<any>(null)
const status = ref<string>('idle')
const jobId = ref<string|undefined>(undefined)
const error = ref<string|null>(null)
const loading = ref(false)

async function load() {
  loading.value = true; error.value = null
  try {
    const [i, m] = await Promise.all([fetch(paths.modelInfo()), fetch(paths.modelMetrics())])
    if (!i.ok || !m.ok) throw new Error('HTTP error')
    info.value = await i.json()
    metrics.value = await m.json()
  } catch (e:any) { error.value = e?.message ?? 'Failed to load model info' }
  finally { loading.value = false }
}

async function retrain() {
  const r = await fetch(paths.modelRetrain(), { method:'POST' })
  if (!r.ok) { alert(`Retrain failed: ${r.status}`); return }
  const data = await r.json()
  jobId.value = data.job_id
  status.value = 'queued'
  poll()
}

async function poll() {
  if (!jobId.value) return
  const r = await fetch(paths.modelStatus(jobId.value))
  if (!r.ok) return
  const d = await r.json()
  status.value = d.state
  if (['queued','running'].includes(status.value)) {
    setTimeout(poll, 1500)
  } else {
    // finished or failed — refresh
    load()
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <header class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold">Model Management</h2>
        <p class="text-slate-500">Active model, metrics, and retraining</p>
      </div>
      <button @click="retrain" class="rounded-md bg-sky-600 text-white px-4 py-2">Retrain</button>
    </header>

    <div v-if="error" class="bg-rose-50 text-rose-700 rounded p-3 text-sm">{{ error }}</div>

    <div class="grid md:grid-cols-2 gap-4">
      <div class="rounded-xl border p-4">
        <div class="text-sm text-slate-500 mb-1">Active Model</div>
        <pre class="text-xs bg-slate-50 p-3 rounded overflow-x-auto">{{ info }}</pre>
      </div>
      <div class="rounded-xl border p-4">
        <div class="text-sm text-slate-500 mb-1">Metrics</div>
        <pre class="text-xs bg-slate-50 p-3 rounded overflow-x-auto">{{ metrics }}</pre>
      </div>
    </div>

    <div v-if="jobId" class="rounded-xl border p-4">
      <div class="text-sm text-slate-500">Training Job</div>
      <div>Job: <code>{{ jobId }}</code></div>
      <div>Status: <b>{{ status }}</b></div>
    </div>
  </div>
</template>