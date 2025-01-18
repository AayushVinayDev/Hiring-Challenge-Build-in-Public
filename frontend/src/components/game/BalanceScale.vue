<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  tiltAngle: number;
}>();

const scaleStyle = computed(() => ({
  transform: `rotate(${props.tiltAngle}deg)`,
}));
</script>

<template>
  <div class="relative w-80 h-80 mx-auto">
    <!-- Fulcrum -->
    <div class="absolute left-1/2 bottom-8 w-4 h-32 bg-gray-800 transform -translate-x-1/2"></div>
    
    <!-- Balance Beam -->
    <div
      class="absolute left-1/2 bottom-36 w-64 h-4 bg-gray-700 transform -translate-x-1/2 origin-center transition-transform duration-500"
      :style="scaleStyle"
    >
      <!-- Left Pan -->
      <div class="absolute -left-8 top-0 w-16 h-16 bg-gray-600 rounded-full transform -translate-y-16 flex items-center justify-center text-white text-xl">
        <slot name="left-pan"></slot>
      </div>
      
      <!-- Right Pan -->
      <div class="absolute -right-8 top-0 w-16 h-16 bg-gray-600 rounded-full transform -translate-y-16 flex items-center justify-center text-white text-xl">
        <slot name="right-pan"></slot>
      </div>
    </div>
  </div>
</template>