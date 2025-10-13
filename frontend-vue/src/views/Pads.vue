<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'

type Pad = {
  id: number | string
  serial_number: string
  pad_type: string
  line_id: number
  belt_id: number
  stage_id: number
  status: string
  created_at: string
  batch_code?: string | null
}

const api = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const rows = ref<Pad[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const page = ref(1)
const pageSize = ref<number>(parseInt(localStorage.getItem('pads_page_size') || '20', 10))
const total = ref(0)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
// ✅ SORTING state
const sortBy = ref<string>('created_at')
const sortDir = ref<'asc' | 'desc'>('desc')
// Filters
const fStatus = ref<string>('')         // '', PASSED, FAILED, IN_PROGRESS
const fType = ref<string>('')           // '', TRANSIT, FREIGHT
const fLine = ref<string>('')           // numeric string
const fBelt = ref<string>('')
const fStage = ref<string>('')
const fQuery = ref<string>('')          // search serial/batch

async function load() {
  loading.value = true
  error.value = null
  try {
    // Pagination, Sorting: included in request
    const params = new URLSearchParams({
      page: String(page.value),
      page_size: String(pageSize.value),
      sort_by: sortBy.value,
      sort_dir: sortDir.value,
    })

    if (fStatus.value) params.append('status', fStatus.value)
    if (fType.value) params.append('pad_type', fType.value)
    if (fLine.value) params.append('line_id', fLine.value)
    if (fBelt.value) params.append('belt_id', fBelt.value)
    if (fStage.value) params.append('stage_id', fStage.value)
    if (fQuery.value) params.append('q', fQuery.value.trim())

    const res = await fetch(`${api}/pads?${params.toString()}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    rows.value = data.items
    total.value = data.total
    // keep server-normalized values (if page capped)
    page.value = data.page // in case backend normalizes it
  } catch (e: any) {
    error.value = e?.message ?? 'Failed to load pads'
  } finally {
    loading.value = false
  }
}

function nextPage() {
  if (page.value < pages.value) {
    page.value += 1
    load()
  }
}
function prevPage() {
  if (page.value > 1) {
    page.value -= 1
    load()
  }
}
function changePageSize(e: Event) {
  const val = parseInt((e.target as HTMLSelectElement).value, 10)
  pageSize.value = val
  localStorage.setItem('pads_page_size', String(val))
  page.value = 1
  load()
}

// SORTING: toggle when clicking a header
function toggleSort(col: string) {
  if (sortBy.value === col) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = col
    sortDir.value = 'asc'
  }
  page.value = 1
  load()
}

function sortGlyph(col: string) {
  if (sortBy.value !== col) return '↕'
  return sortDir.value === 'asc' ? '↑' : '↓'
}

function resetFilters() {
  fStatus.value = ''
  fType.value = ''
  fLine.value = ''
  fBelt.value = ''
  fStage.value = ''
  fQuery.value = ''
  page.value = 1
  load()
}

// if page size changes elsewhere, reload
watch(pageSize, () => { page.value = 1; load() })

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <!-- Header / Controls -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-xl font-semibold">Pads</h2>
        <p class="text-slate-500">Sort by column headers; filter by status/type/line/belt/stage; search serial or batch</p>
      </div>

      <div class="flex items-center gap-3">
        <label class="text-sm text-slate-600">Rows per page:</label>
        <select
          class="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
          :value="pageSize"
          @change="changePageSize"
        >
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="30">30</option>
          <option :value="50">50</option>
        </select>

        <button @click="load" class="rounded-lg border border-slate-300 px-3 py-1.5 hover:bg-slate-100">
          Refresh
        </button>
      </div>
    </div>

     <!-- Filters row -->
    <div class="flex flex-wrap gap-2 items-end">
      <div class="flex flex-col">
        <label class="text-xs text-slate-500">Status</label>
        <select v-model="fStatus" class="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm min-w-[140px]">
          <option value="">All</option>
          <option value="PASSED">PASSED</option>
          <option value="FAILED">FAILED</option>
          <option value="IN_PROGRESS">IN_PROGRESS</option>
        </select>
      </div>

      <div class="flex flex-col">
        <label class="text-xs text-slate-500">Type</label>
        <select v-model="fType" class="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm min-w-[140px]">
          <option value="">All</option>
          <option value="TRANSIT">TRANSIT</option>
          <option value="FREIGHT">FREIGHT</option>
        </select>
      </div>

      <div class="flex flex-col">
        <label class="text-xs text-slate-500">Line</label>
        <input v-model="fLine" type="number" min="1" class="rounded-md border border-slate-300 px-2 py-1 text-sm w-24" />
      </div>

      <div class="flex flex-col">
        <label class="text-xs text-slate-500">Belt</label>
        <input v-model="fBelt" type="number" min="1" class="rounded-md border border-slate-300 px-2 py-1 text-sm w-24" />
      </div>

      <div class="flex flex-col">
        <label class="text-xs text-slate-500">Stage</label>
        <input v-model="fStage" type="number" min="1" class="rounded-md border border-slate-300 px-2 py-1 text-sm w-24" />
      </div>

      <div class="flex flex-col flex-1 min-w-[220px]">
        <label class="text-xs text-slate-500">Search (serial or batch)</label>
        <input v-model="fQuery" type="text" placeholder="e.g., TR-01 or BC-"
               class="rounded-md border border-slate-300 px-2 py-1 text-sm w-full" />
      </div>

      <div class="flex gap-2">
        <button @click="page = 1; load()" class="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-100">
          Apply
        </button>
        <button @click="resetFilters" class="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-100">
          Reset
        </button>
      </div>
    </div>

    <!-- Errors -->
    <div v-if="error" class="rounded-lg bg-rose-50 p-3 text-rose-700 text-sm">
      {{ error }}
    </div>

    <!-- Table -->
    <div class="rounded-2xl border bg-white p-4 shadow-sm overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-500 select-none">
            <th class="py-2 pr-3 cursor-pointer" @click="toggleSort('serial_number')">
              Serial <span class="ml-1 opacity-60">{{ sortGlyph('serial_number') }}</span>
            </th>
            <th class="py-2 pr-3 cursor-pointer" @click="toggleSort('pad_type')">
              Type <span class="ml-1 opacity-60">{{ sortGlyph('pad_type') }}</span>
            </th>
            <th class="py-2 pr-3 cursor-pointer" @click="toggleSort('line_id')">
              Line <span class="ml-1 opacity-60">{{ sortGlyph('line_id') }}</span>
            </th>
            <th class="py-2 pr-3 cursor-pointer" @click="toggleSort('belt_id')">
              Belt <span class="ml-1 opacity-60">{{ sortGlyph('belt_id') }}</span>
            </th>
            <th class="py-2 pr-3 cursor-pointer" @click="toggleSort('stage_id')">
              Stage <span class="ml-1 opacity-60">{{ sortGlyph('stage_id') }}</span>
            </th>
            <th class="py-2 pr-3 cursor-pointer" @click="toggleSort('status')">
              Status <span class="ml-1 opacity-60">{{ sortGlyph('status') }}</span>
            </th>
            <th class="py-2 pr-3 cursor-pointer" @click="toggleSort('batch_code')">
              Batch <span class="ml-1 opacity-60">{{ sortGlyph('batch_code') }}</span>
            </th>
            <th class="py-2 pr-3 cursor-pointer" @click="toggleSort('created_at')">
              Created <span class="ml-1 opacity-60">{{ sortGlyph('created_at') }}</span>
            </th>
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
            <td class="py-2 pr-3">{{ r.batch_code ?? '—' }}</td>
            <td class="py-2 pr-3">{{ new Date(r.created_at).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="loading" class="py-4 text-slate-500">Loading…</div>
      <div v-else-if="rows.length === 0" class="py-4 text-slate-500">No pads found.</div>
    </div>

    <!-- Pagination controls -->
    <div class="flex flex-col items-center gap-2 sm:flex-row sm:justify-between">
      <div class="text-sm text-slate-600">
        Showing
        <span class="font-medium">{{ rows.length ? (page - 1) * pageSize + 1 : 0 }}</span>
        –
        <span class="font-medium">{{ Math.min(page * pageSize, total) }}</span>
        of <span class="font-medium">{{ total }}</span> pads
      </div>

      <div class="flex items-center gap-2">
        <button class="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-100 disabled:opacity-50"
                :disabled="page <= 1" @click="prevPage">
          ← Prev
        </button>
        <span class="text-sm text-slate-600">Page {{ page }} of {{ pages }}</span>
        <button class="rounded-md border px-3 py-1.5 text-sm hover:bg-slate-100 disabled:opacity-50"
                :disabled="page >= pages" @click="nextPage">
          Next →
        </button>
      </div>
    </div>
  </div>
</template>