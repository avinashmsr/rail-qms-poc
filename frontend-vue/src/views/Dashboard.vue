<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'

type LineStat = { line: string; total: number; passed: number; failed: number; in_progress: number }

const api = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const loading = ref(true)
const error = ref<string | null>(null)
const stats = ref<LineStat[]>([])

async function load() {
  loading.value = true; error.value = null
  try {
    const res = await fetch(`${api}/stats/lines`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    stats.value = await res.json()
  } catch (e: any) {
    error.value = e?.message ?? 'Failed to load'
  } finally {
    loading.value = false
  }
}

async function generateDemo() {
  try {
    const res = await fetch(`${api}/setup/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ count: 150, lines: 2, belts_per_line: 3 }),
  })
  if (!res.ok) {
    const txt = await res.text()
    console.error('generate API call failed:', txt)
    return
  }
  await load() // <-- refresh totals
  } catch (e) {
    console.error(e)
  }
}

const totals = computed(() => {
  return stats.value.reduce(
    (acc, s) => {
      acc.total += s.total
      acc.passed += s.passed
      acc.failed += s.failed
      acc.in_progress += s.in_progress
      return acc
    },
    { total: 0, passed: 0, failed: 0, in_progress: 0 }
  )
})

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <!-- Actions -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold tracking-tight">Dashboard</h2>
        <p class="text-slate-500">Assembly line quality at a glance</p>
      </div>
      <div class="flex gap-2">
        <button @click="load"
                class="px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-100">
          Refresh
        </button>
        <button @click="generateDemo"
                class="px-4 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700">
          Generate Demo Data
        </button>
      </div>
    </div>

    <!-- Summary cards -->
    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div class="rounded-2xl border bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">Total pads</div>
        <div class="mt-1 text-3xl font-semibold">{{ totals.total }}</div>
      </div>
      <div class="rounded-2xl border bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">Passed</div>
        <div class="mt-1 text-3xl font-semibold text-emerald-600">{{ totals.passed }}</div>
      </div>
      <div class="rounded-2xl border bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">Failed</div>
        <div class="mt-1 text-3xl font-semibold text-rose-600">{{ totals.failed }}</div>
        <div class="mt-2 h-2 rounded bg-rose-100">
          <div class="h-2 rounded bg-rose-500"
               :style="{ width: (totals.total ? Math.min(100, Math.round((totals.failed / totals.total) * 100)) : 0) + '%' }"></div>
        </div>
      </div>
      <div class="rounded-2xl border bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">In-progress</div>
        <div class="mt-1 text-3xl font-semibold text-sky-600">{{ totals.in_progress }}</div>
      </div>
    </div>

    <!-- Per-line table -->
    <div class="rounded-2xl border bg-white p-4 shadow-sm">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-semibold">By line</h3>
        <span v-if="loading" class="text-sm text-slate-500">Loading…</span>
      </div>

      <div v-if="error" class="mt-3 rounded-lg bg-rose-50 text-rose-700 p-3 text-sm">
        {{ error }}
      </div>

      <div v-else class="mt-3 overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-slate-500">
              <th class="py-2 pr-4 font-medium">Line</th>
              <th class="py-2 pr-4 font-medium">Total</th>
              <th class="py-2 pr-4 font-medium">Passed</th>
              <th class="py-2 pr-4 font-medium">Failed</th>
              <th class="py-2 pr-4 font-medium">In-progress</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in stats" :key="s.line" class="border-t">
              <td class="py-3 pr-4 font-medium">{{ s.line }}</td>
              <td class="py-3 pr-4">{{ s.total }}</td>
              <td class="py-3 pr-4 text-emerald-700">{{ s.passed }}</td>
              <td class="py-3 pr-4 text-rose-700">{{ s.failed }}</td>
              <td class="py-3 pr-4 text-sky-700">{{ s.in_progress }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="!loading && stats.length === 0" class="py-6 text-slate-500">
          No data yet — seed `/setup/seed` or click <b>Generate Demo Data</b>.
        </div>
      </div>
    </div>
  </div>
</template>