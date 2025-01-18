<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  message: string;
  type: 'success' | 'error' | 'info';
  show: boolean;
}>();

const isVisible = ref(false);

watch(() => props.show, (newValue) => {
  isVisible.value = newValue;
  if (newValue) {
    setTimeout(() => {
      isVisible.value = false;
    }, 3000);
  }
});

const messageClass = computed(() => ({
  'bg-green-500': props.type === 'success',
  'bg-red-500': props.type === 'error',
  'bg-blue-500': props.type === 'info',
}));
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform -translate-y-2 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100"
    leave-to-class="transform -translate-y-2 opacity-0"
  >
    <div
      v-if="isVisible"
      class="fixed bottom-4 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg text-white shadow-lg"
      :class="messageClass"
    >
      {{ message }}
    </div>
  </Transition>
</template>