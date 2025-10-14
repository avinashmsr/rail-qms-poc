<script setup lang="ts">
import { ref } from 'vue'
import { paths } from '@/api'

type Expl = { feature: string; value?: number; contribution?: number }
type XAIRes = {
  local_explanation?: Expl[]   // per-pad (e.g., SHAP values)
  global_importance?: Expl[]   // model-level importance
  baseline_probability?: number
}

const padId = ref('')
const loading = ref(false)
const error = ref<string|null>(null)
const data = ref<XAIRes|null>(null)

async function load() {
  loading.value = true; error.value = null; data.value = null
  try {
    if (!padId.value) throw new Error('Provide a Pad ID')
    const r = await fetch(paths.xaiByPad(padId.value))
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    data.value = await r.json()
  } catch (e:any) { error.value = e?.message ?? 'Failed to load XAI' }
  finally { loading.value = false }
}
</script>

<template>
  <div class="space-y-6">
    <header>
      <h2 class="text-xl font-semibold">Explainable AI</h2>
      <p class="text-slate-500">Per-pad local explanation and global feature importance</p>
    </header>

    <div class="flex items-end gap-3">
      <label class="text-sm">Pad ID
        <input v-model="padId" class="border rounded px-2 py-1" placeholder="UUID or serial"/>
      </label>
      <button @click="load" class="rounded-md bg-sky-600 text-white px-4 py-2" :disabled="loading">Explain</button>
    </div>

    <div v-if="error" class="bg-rose-50 text-rose-700 rounded p-3 text-sm">{{ error }}</div>

    <div v-if="data" class="grid md:grid-cols-2 gap-4">
      <div class="rounded-xl border p-4">
        <div class="text-sm text-slate-500 mb-2">Local (this pad)</div>
        <div v-if="!data.local_explanation?.length" class="text-slate-500 text-sm">No local explanation.</div>
        <div v-else class="space-y-2">
          <div v-for="e in data.local_explanation" :key="e.feature" class="flex items-center gap-2">
            <div class="w-40 text-sm">{{ e.feature }}</div>
            <div class="flex-1 bg-slate-100 h-2 rounded">
              <div class="h-2 rounded bg-emerald-500" :style="{ width: Math.min(100, Math.abs(e.contribution||0)*100) + '%' }"></div>
            </div>
            <div class="w-12 text-right text-xs">{{ ((e.contribution||0)*100).toFixed(0) }}%</div>
          </div>
        </div>
      </div>

      <div class="rounded-xl border p-4">
        <div class="text-sm text-slate-500 mb-2">Global importance</div>
        <div v-if="!data.global_importance?.length" class="text-slate-500 text-sm">No global importance.</div>
        <div v-else class="space-y-2">
          <div v-for="e in data.global_importance" :key="e.feature" class="flex items-center gap-2">
            <div class="w-40 text-sm">{{ e.feature }}</div>
            <div class="flex-1 bg-slate-100 h-2 rounded">
              <div class="h-2 rounded bg-indigo-500" :style="{ width: Math.min(100, Math.abs(e.value||0)*100) + '%' }"></div>
            </div>
            <div class="w-12 text-right text-xs">{{ ((e.value||0)*100).toFixed(0) }}%</div>
          </div>
        </div>
      </div>

      <div v-if="data.baseline_probability !== undefined" class="rounded-xl border p-4 md:col-span-2">
        <div class="text-sm text-slate-500">Baseline probability</div>
        <div class="text-2xl font-semibold">{{ Math.round((data.baseline_probability||0)*100) }}%</div>
      </div>
    </div>
  </div>
</template>