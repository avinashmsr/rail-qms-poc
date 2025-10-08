<script setup lang="ts">
import { onMounted, ref } from 'vue'
const rows = ref<any[]>([])
onMounted(async () => {
  const api = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const res = await fetch(`${api}/pads`)
  rows.value = await res.json()
})
</script>

<template>
  <div style="padding:16px">
    <h2>Brake Pads</h2>
    <table style="width:100%; border-collapse:collapse">
      <thead>
        <tr>
          <th align="left">Serial</th>
          <th>Type</th>
          <th>Line</th>
          <th>Belt</th>
          <th>Stage</th>
          <th>Status</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id" style="border-top:1px solid #eee">
          <td>{{ r.serial_number }}</td>
          <td align="center">{{ r.pad_type }}</td>
          <td align="center">{{ r.line_id }}</td>
          <td align="center">{{ r.belt_id }}</td>
          <td align="center">{{ r.stage_id }}</td>
          <td align="center">{{ r.status }}</td>
          <td align="center">{{ new Date(r.created_at).toLocaleString() }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>