<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchLineStats } from '../api'
const stats = ref<any[]>([])

onMounted(async ()=> { stats.value = await fetchLineStats() })
</script>
<template>

</template>