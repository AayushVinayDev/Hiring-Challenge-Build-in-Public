<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
      <div class="text-center">
        <h1 class="text-3xl font-bold">Welcome to Balance Game</h1>
        <p class="mt-2 text-gray-600">Choose your role to continue</p>
      </div>
      
      <div class="space-y-4">
        <button
          @click="router.push('/student/login')"
          class="w-full btn-primary bg-blue-500"
        >
          I'm a Student
        </button>
        
        <button
          @click="router.push('/teacher/login')"
          class="w-full btn-primary bg-green-500 hover:bg-green-600"
        >
          I'm a Teacher
        </button>
      </div>
    </div>
  </div>
</template>