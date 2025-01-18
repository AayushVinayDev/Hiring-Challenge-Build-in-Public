<script setup lang="ts">
defineProps<{
  progress: number;
  level: number;
}>();
</script>

<template>
  <div class="w-full max-w-md">
    <div class="flex justify-between items-center mb-2">
      <span class="text-sm font-semibold">Level {{ level }}</span>
      <span class="text-sm">{{ Math.round(progress * 100) }}%</span>
    </div>
    <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
      <div
        class="h-full bg-blue-500 transition-all duration-300"
        :style="{ width: `${progress * 100}%` }"
      ></div>
    </div>
  </div>
</template>