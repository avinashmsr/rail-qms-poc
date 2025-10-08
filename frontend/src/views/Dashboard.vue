<script setup lang="ts">
import { onMounted, ref } from 'vue'
const stats = ref<any[]>([])
onMounted(async () => {
  const api = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const res = await fetch(`${api}/stats/lines`)
  stats.value = await res.json()
})
</script>

<template>
  <div style="padding:16px">
    <h2>Assembly Lines</h2>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px,1fr)); gap:12px">
      <div v-for="(s,i) in stats" :key="i" style="border:1px solid #ddd; border-radius:12px; padding:16px">
        <h3 style="margin-top:0">{{ s.line }}</h3>
        <p>Total: {{ s.total }}</p>
        <p>Passed: {{ s.passed }} | Failed: {{ s.failed }} | In-progress: {{ s.in_progress }}</p>
      </div>
      <div v-if="!stats || stats.length === 0" style="opacity:0.7">No data yet (did you seed?).</div>
    </div>
  </div>
</template>