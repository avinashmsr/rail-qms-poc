<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { paths } from '@/api'

type ReviewItem = {
  id: string|number
  pad_id?: string
  serial_number?: string
  model_decision?: string
  probability?: number
  reason?: string
  created_at?: string
}

const items = ref<ReviewItem[]>([])
const loading = ref(false)
const error = ref<string|null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const status = ref<'PENDING'|'RESOLVED'|'OVERRIDDEN'>('PENDING')

async function load() {
  loading.value = true; error.value = null
  try {
    const r = await fetch(paths.reviewsList(status.value, page.value, pageSize.value))
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const data = await r.json()
    items.value = data.items || []
    total.value = data.total || items.value.length
  } catch (e:any) { error.value = e?.message ?? 'Failed to load reviews' }
  finally { loading.value = false }
}

async function act(id: string|number, action: 'approve'|'reject'|'override') {
  const note = prompt(`${action.toUpperCase()} — optional note:`) || undefined
  const r = await fetch(paths.reviewAction(id, action), { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ note }) })
  if (!r.ok) { alert(`Action failed: ${r.status}`); return }
  await load()
}

function next(){ if(page.value < pages.value){ page.value++; load() } }
function prev(){ if(page.value > 1){ page.value--; load() } }

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <header class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold">Expert Review Queue</h2>
        <p class="text-slate-500">Approve/override/reject model decisions</p>
      </div>
      <div class="flex gap-2">
        <select v-model="status" class="border rounded px-2 py-1 text-sm" @change="page=1; load()">
          <option value="PENDING">PENDING</option>
          <option value="RESOLVED">RESOLVED</option>
          <option value="OVERRIDDEN">OVERRIDDEN</option>
        </select>
        <button @click="load" class="border rounded px-3 py-1.5">Refresh</button>
      </div>
    </header>

    <div v-if="error" class="bg-rose-50 text-rose-700 p-3 rounded text-sm">{{ error }}</div>

    <div class="rounded-2xl border bg-white p-4 shadow-sm overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-500">
            <th class="py-2 pr-3">Pad</th>
            <th class="py-2 pr-3">Decision</th>
            <th class="py-2 pr-3">Confidence</th>
            <th class="py-2 pr-3">Reason</th>
            <th class="py-2 pr-3">Created</th>
            <th class="py-2 pr-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="it in items" :key="it.id" class="border-t">
            <td class="py-2 pr-3">{{ it.serial_number ?? it.pad_id }}</td>
            <td class="py-2 pr-3">{{ it.model_decision }}</td>
            <td class="py-2 pr-3">{{ it.probability !== undefined ? Math.round((it.probability||0)*100)+'%' : '—' }}</td>
            <td class="py-2 pr-3 max-w-[320px] truncate" :title="it.reason">{{ it.reason ?? '—' }}</td>
            <td class="py-2 pr-3">{{ it.created_at ? new Date(it.created_at).toLocaleString() : '—' }}</td>
            <td class="py-2 pr-3">
              <div class="flex gap-2">
                <button class="rounded border px-2 py-1" @click="act(it.id,'approve')">Approve</button>
                <button class="rounded border px-2 py-1" @click="act(it.id,'override')">Override</button>
                <button class="rounded border px-2 py-1" @click="act(it.id,'reject')">Reject</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && items.length===0" class="text-slate-500 py-3">No items.</div>
    </div>

    <div class="flex items-center justify-between">
      <div class="text-sm text-slate-600">Page {{ page }} of {{ pages }}</div>
      <div class="flex gap-2">
        <button class="border rounded px-3 py-1.5" :disabled="page<=1" @click="prev">← Prev</button>
        <button class="border rounded px-3 py-1.5" :disabled="page>=pages" @click="next">Next →</button>
      </div>
    </div>
  </div>
</template>