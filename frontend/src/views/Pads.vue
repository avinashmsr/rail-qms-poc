<script setup lang="ts">
import { onMounted, ref } from 'vue'
type Pad = {
  id: number; serial_number: string; pad_type: string;
  line_id: number; belt_id: number; stage_id: number;
  status: string; created_at: string;
}
const api = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const rows = ref<Pad[]>([])
const loading = ref(true)
async function load() {
  loading.value = true
  const res = await fetch(`${api}/pads`)
  rows.value = await res.json()
  loading.value = false
}
onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold">Pads</h2>
        <p class="text-slate-500">Latest 500 pads across all lines</p>
      </div>
      <button @click="load" class="px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-100">
        Refresh
      </button>
    </div>

    <div class="rounded-2xl border bg-white p-4 shadow-sm overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-500">
            <th class="py-2 pr-3">Serial</th>
            <th class="py-2 pr-3">Type</th>
            <th class="py-2 pr-3">Line</th>
            <th class="py-2 pr-3">Belt</th>
            <th class="py-2 pr-3">Stage</th>
            <th class="py-2 pr-3">Status</th>
            <th class="py-2 pr-3">Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id" class="border-t">
            <td class="py-2 pr-3 font-medium">{{ r.serial_number }}</td>
            <td class="py-2 pr-3">{{ r.pad_type }}</td>
            <td class="py-2 pr-3">{{ r.line_id }}</td>
            <td class="py-2 pr-3">{{ r.belt_id }}</td>
            <td class="py-2 pr-3">{{ r.stage_id }}</td>
            <td class="py-2 pr-3">
              <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs"
                    :class="{
                      'bg-emerald-100 text-emerald-700': r.status==='PASSED',
                      'bg-rose-100 text-rose-700': r.status==='FAILED',
                      'bg-sky-100 text-sky-700': r.status==='IN_PROGRESS',
                    }">
                {{ r.status.replace('_',' ') }}
              </span>
            </td>
            <td class="py-2 pr-3">{{ new Date(r.created_at).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading" class="py-6 text-slate-500">Loading…</div>
      <div v-else-if="rows.length===0" class="py-6 text-slate-500">No pads yet.</div>
    </div>
  </div>
</template>