<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { paths } from '@/api'

type TopFactor = { feature: string; impact: number }
type MaterialMix = {
  resin_pct?: number; fiber_pct?: number; metal_powder_pct?: number; filler_pct?: number;
  abrasives_pct?: number; binder_pct?: number;
  temp_c?: number; pressure_mpa?: number; cure_time_s?: number; moisture_pct?: number;
}

type PredictRes = {
  label?: string
  score?: number
  confidence?: number
  explanation?: Record<string, number>
  model_version?: string

  // normalized
  quality: string
  probability: number
  top_factors: TopFactor[]
  recommendations?: string[]

  // NEW: only present for /predict/pad
  pad?: { id: string; serial_number?: string }
  material_mix?: MaterialMix
  source: 'mix' | 'pad'
}

const mode = ref<'mix'|'pad'>('mix')

// material mix form
const form = ref({
  resin_pct: 18, fiber_pct: 12, metal_powder_pct: 22, filler_pct: 28,
  abrasives_pct: 10, binder_pct: 10,
  temp_c: 120, pressure_mpa: 12, cure_time_s: 2400, moisture_pct: 0.4
})
const padId = ref<string>('')

const loading = ref(false)
const error = ref<string|null>(null)
const result = ref<PredictRes | null>(null)

const EPS = 0.01 // small tolerance for floating rounding

const totalPct = computed(() => {
  const m = form.value
  return (
    Number(m.resin_pct || 0) +
    Number(m.fiber_pct || 0) +
    Number(m.metal_powder_pct || 0) +
    Number(m.filler_pct || 0) +
    Number(m.abrasives_pct || 0) +
    Number(m.binder_pct || 0)
  )
})
const remainingPct = computed(() => 100 - totalPct.value)
const mixPctValid = computed(() => Math.abs(remainingPct.value) <= EPS)
const mixPctOver  = computed(() => remainingPct.value < -EPS)
const mixPctUnder = computed(() => remainingPct.value >  EPS)

// Predict is disabled when:
// - MIX mode and sum != 100
// - PAD mode and no padId
const canPredict = computed(() => {
  if (mode.value === 'mix') return mixPctValid.value
  return !!padId.value?.trim()
})

// 🔹 Clear outputs when switching tabs
watch(mode, () => {
  result.value = null
  error.value = null
})

//Normalize function remembers current UI state
function normalize(raw: any, source: 'mix' | 'pad'): PredictRes {
  const quality = raw.quality ?? raw.label ?? 'UNKNOWN'
  const risk = typeof raw.score === 'number' ? raw.score : NaN
  const probability =
    typeof raw.confidence === 'number'
      ? raw.confidence
      : typeof raw.probability === 'number'
        ? raw.probability
        : Number.isFinite(risk)
          ? (String(quality).toUpperCase() === 'FAIL' ? risk : 1 - risk)
          : NaN

  const exp = raw.explanation ?? {}
  const top_factors: TopFactor[] = Array.isArray(exp)
    ? exp
    : Object.entries(exp).map(([feature, impact]) => ({
      feature,
      impact: Number(impact) || 0
    }))

  top_factors.sort((a,b)=>Math.abs(b.impact)-Math.abs(a.impact))

  return {
    label: raw.label,
    score: raw.score,
    confidence: raw.confidence,
    explanation: raw.explanation,
    model_version: raw.model_version,
    quality,
    probability,
    top_factors,
    recommendations: raw.recommendations ?? [],
    pad: raw.pad,                                  // NEW
    material_mix: raw.material_mix as MaterialMix, // NEW
    source,                          // ← record source
  }
}

async function submit() {
  loading.value = true
  error.value = null
  // result.value = null --- (don't clear result here; we want to keep last result until new one arrives)
  try {
    let res: Response
    if (mode.value === 'mix') {
      res = await fetch(paths.predictByMix(), {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(form.value)
      })
    } else {
      if (!padId.value) throw new Error('Provide a Pad ID')
      res = await fetch(paths.predictByPad(padId.value))
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const raw = await res.json()
    result.value = normalize(raw, mode.value)   // ← pass active tab as source
  } catch (e:any) {
    error.value = e?.message ?? 'Prediction failed'
  } finally {
    loading.value = false
  }
}

// helper to normalize the label and choose badge colors
function normQuality(q: string | undefined | null) {
  return String(q ?? 'UNKNOWN').toUpperCase().replace('-', '_')
}
function badgeClasses(q: string | undefined | null) {
  switch (normQuality(q)) {
    case 'PASS':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200'
    case 'FAIL':
      return 'bg-rose-100 text-rose-800 border-rose-200'
    case 'AT_RISK':
      return 'bg-amber-100 text-amber-800 border-amber-200'
    default:
      return 'bg-slate-100 text-slate-700 border-slate-200'
  }
}

</script>

<template>
  <div class="space-y-6">
    <header>
      <h2 class="text-xl font-semibold">AI Prediction</h2>
      <p class="text-slate-500">Predict quality from material mix or by selecting a Pad</p>
    </header>

    <div class="flex gap-3">
      <button class="rounded-md border px-3 py-1.5" :class="{'bg-slate-900 text-white': mode==='mix'}" @click="mode='mix'">By Material Mix</button>
      <button class="rounded-md border px-3 py-1.5" :class="{'bg-slate-900 text-white': mode==='pad'}" @click="mode='pad'">By Pad</button>
    </div>

    <div v-if="mode==='mix'" class="grid grid-cols-2 md:grid-cols-3 gap-3">
      <label class="text-sm">Resin % <input v-model.number="form.resin_pct" type="number" step="0.1" min="0" max="100" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Fiber % <input v-model.number="form.fiber_pct" type="number" step="0.1" min="0" max="100" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Metal powder % <input v-model.number="form.metal_powder_pct" type="number" step="0.1" min="0" max="100" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Filler % <input v-model.number="form.filler_pct" type="number" step="0.1" min="0" max="100" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Abrasives % <input v-model.number="form.abrasives_pct" type="number" step="0.1" min="0" max="100" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Binder % <input v-model.number="form.binder_pct" type="number" step="0.1" min="0" max="100" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Mix temp (°C) <input v-model.number="form.temp_c" type="number" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Press (MPa) <input v-model.number="form.pressure_mpa" type="number" step="0.1" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Cure time (s) <input v-model.number="form.cure_time_s" type="number" class="w-full border rounded px-2 py-1"></label>
      <label class="text-sm">Moisture % <input v-model.number="form.moisture_pct" type="number" step="0.01" class="w-full border rounded px-2 py-1"></label>

      <!-- validation helper under the grid -->
<div class="col-span-full text-sm"
     :class="{
       'text-emerald-700': mixPctValid,
       'text-amber-700': mixPctUnder,
       'text-rose-700': mixPctOver
     }"
     aria-live="polite">
  <template v-if="mixPctValid">
    ✅ Total = {{ totalPct.toFixed(1) }}% (OK)
  </template>
  <template v-else-if="mixPctUnder">
    ⚠️ Total = {{ totalPct.toFixed(1) }}% — {{ Math.abs(remainingPct).toFixed(1) }}% remaining to reach 100%
  </template>
  <template v-else>
    ⚠️ Total = {{ totalPct.toFixed(1) }}% — over by {{ Math.abs(remainingPct).toFixed(1) }}%
  </template>
</div>
    </div>

    <div v-else class="flex items-end gap-3">
      <label class="text-sm">Pad ID
        <input v-model="padId" placeholder="e.g. TR-01-03-00001 or UUID" class="border rounded px-2 py-1">
      </label>
    </div>

<!-- Predict button -->
<div class="flex gap-2">
  <button
    @click="submit"
    class="rounded-md px-4 py-2 text-white"
    :class="canPredict ? 'bg-sky-600 hover:bg-sky-700' : 'bg-slate-300 cursor-not-allowed'"
    :disabled="!canPredict"
  >
    Predict
  </button>
  <div v-if="loading" class="text-slate-500">Predicting…</div>
</div>

    <div v-if="error" class="rounded-md bg-rose-50 text-rose-700 p-3 text-sm">{{ error }}</div>

    <!-- RESULTS: only show when result belongs to active tab -->
    <div v-if="result && result.source === mode" class="grid gap-4 md:grid-cols-3">
      <div class="rounded-xl border p-4">
        <div class="text-sm text-slate-500">Prediction</div>
        <div class="mt-2 flex items-center gap-3">
          <span class="text-2xl font-semibold">{{ normQuality(result!.quality) }}</span>
          <span 
          class="inline-flex items-center rounded-full border px-2 py-0.5 text-xs"
          :class="badgeClasses(result!.quality)"
          >
          {{ normQuality(result!.quality).replace('_', ' ') }}
        </span>
      </div>
  <div class="mt-1 text-slate-500">
    Confidence:
    {{ Number.isFinite(result!.probability) ? Math.round(result!.probability * 100) : '—' }}%
  </div>

  <div v-if="result!.model_version" class="mt-1 text-xs text-slate-500">
    Model: <code class="text-slate-700">{{ result!.model_version }}</code>
  </div>
</div>

      <div class="rounded-xl border p-4 md:col-span-2" v-if="result.top_factors?.length">
        <div class="text-sm text-slate-500 mb-2">Top contributing factors</div>
        <div class="space-y-2">
          <div v-for="f in result.top_factors" :key="f.feature" class="flex items-center gap-2">
            <div class="w-40 text-sm">{{ f.feature }}</div>
            <div class="flex-1 bg-slate-100 h-2 rounded">
              <div class="h-2 rounded bg-sky-500" :style="{ width: Math.min(100, Math.abs(f.impact)*100) + '%' }"></div>
            </div>
            <div class="w-12 text-right text-xs">{{ (f.impact*100).toFixed(0) }}%</div>
          </div>
        </div>
      </div>

      <div class="rounded-xl border p-4 md:col-span-3" v-if="result.recommendations?.length">
        <div class="text-sm text-slate-500 mb-2">Recommendations</div>
        <ul class="list-disc pl-5">
          <li v-for="(r, i) in result.recommendations" :key="i">{{ r }}</li>
        </ul>
      </div>
    </div>
    <!-- Material Mix Used (shown when backend provided it, i.e., By Pad) -->
<div v-if="result?.material_mix" class="rounded-xl border p-4 md:col-span-2">
  <div class="text-sm text-slate-500 mb-2">
    Material mix used
    <span v-if="result?.pad?.serial_number" class="ml-2 text-xs text-slate-600">
      (Pad: {{ result.pad.serial_number }})
    </span>
  </div>

  <div class="grid grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-2 text-sm">
    <div><span class="text-slate-500">Resin %</span> <span class="ml-2 font-medium">{{ result.material_mix!.resin_pct }}</span></div>
    <div><span class="text-slate-500">Fiber %</span> <span class="ml-2 font-medium">{{ result.material_mix!.fiber_pct }}</span></div>
    <div><span class="text-slate-500">Metal powder %</span> <span class="ml-2 font-medium">{{ result.material_mix!.metal_powder_pct }}</span></div>
    <div><span class="text-slate-500">Filler %</span> <span class="ml-2 font-medium">{{ result.material_mix!.filler_pct }}</span></div>
    <div><span class="text-slate-500">Abrasives %</span> <span class="ml-2 font-medium">{{ result.material_mix!.abrasives_pct }}</span></div>
    <div><span class="text-slate-500">Binder %</span> <span class="ml-2 font-medium">{{ result.material_mix!.binder_pct }}</span></div>
    <div><span class="text-slate-500">Mix temp (°C)</span> <span class="ml-2 font-medium">{{ result.material_mix!.temp_c }}</span></div>
    <div><span class="text-slate-500">Press (MPa)</span> <span class="ml-2 font-medium">{{ result.material_mix!.pressure_mpa }}</span></div>
    <div><span class="text-slate-500">Cure time (s)</span> <span class="ml-2 font-medium">{{ result.material_mix!.cure_time_s }}</span></div>
    <div><span class="text-slate-500">Moisture %</span> <span class="ml-2 font-medium">{{ result.material_mix!.moisture_pct }}</span></div>
  </div>
</div>

  </div>
</template>