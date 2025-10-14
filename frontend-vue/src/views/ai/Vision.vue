<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { paths } from '@/api'

type BBox = [number, number, number, number] // x, y, w, h (fraction 0..1 or pixels; backend decides)
type Defect = { label: string; score: number; bbox: BBox }
type Item = { pad_id: string; pad_type?: string; image_url: string; defects: Defect[] }

const items = ref<Item[]>([])
const loading = ref(false)
const error = ref<string|null>(null)

const limit = ref(20)
const label = ref('')
const minScore = ref(0.3)
const showOnlyDefective = ref(true)

async function load() {
  loading.value = true; error.value = null
  try {
    const r = await fetch(paths.cvDefects(limit.value, label.value, minScore.value))
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const all: Item[] = await r.json()
    items.value = showOnlyDefective.value ? all.filter(i => (i.defects?.length||0) > 0) : all
  } catch (e:any) { error.value = e?.message ?? 'Failed to load defects' }
  finally { loading.value = false }
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <header class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold">Vision: Defect Detection</h2>
        <p class="text-slate-500">AI detections over synthetic images</p>
      </div>
      <button @click="load" class="border rounded px-3 py-1.5">Refresh</button>
    </header>

    <div class="flex flex-wrap gap-3 items-end">
      <label class="text-sm">Limit
        <input v-model.number="limit" type="number" min="1" class="border rounded px-2 py-1 w-24">
      </label>
      <label class="text-sm">Label
        <input v-model="label" placeholder="crack / chip / ..." class="border rounded px-2 py-1 w-40">
      </label>
      <label class="text-sm">Min score
        <input v-model.number="minScore" type="number" step="0.05" min="0" max="1" class="border rounded px-2 py-1 w-24">
      </label>
      <label class="text-sm inline-flex items-center gap-2">
        <input type="checkbox" v-model="showOnlyDefective">
        Show only items with defects
      </label>
    </div>

    <div v-if="error" class="bg-rose-50 text-rose-700 p-3 rounded text-sm">{{ error }}</div>

    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="it in items" :key="it.pad_id" class="rounded-xl border p-3 bg-white">
        <div class="flex justify-between text-sm mb-2">
          <div class="font-medium">Pad {{ it.pad_id }}</div>
          <div class="text-slate-500">{{ it.pad_type ?? '' }}</div>
        </div>

        <div class="relative">
          <img :src="it.image_url" class="w-full rounded-lg border" />
          <template v-for="(d, idx) in it.defects" :key="idx">
            <div class="absolute border-2 border-rose-500 rounded"
                 :style="{
                   left: (Array.isArray(d.bbox) ? d.bbox[0] : 0) + 'px',
                   top:  (Array.isArray(d.bbox) ? d.bbox[1] : 0) + 'px',
                   width:(Array.isArray(d.bbox) ? d.bbox[2] : 0) + 'px',
                   height:(Array.isArray(d.bbox) ? d.bbox[3] : 0) + 'px',
                 }"></div>
            <div class="absolute bg-rose-600 text-white text-xs px-1 rounded"
                 :style="{ left: (d.bbox[0]) + 'px', top: Math.max(0, d.bbox[1]-16) + 'px' }">
              {{ d.label }} ({{ Math.round(d.score*100) }}%)
            </div>
          </template>
        </div>
      </div>
    </div>

    <div v-if="!loading && items.length===0" class="text-slate-500">No items to display.</div>
  </div>
</template>