<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const name = ref('');
const email = ref('');
const password = ref('');

const handleSignup = async () => {
  try {
    await authStore.signup({
      name: name.value,
      email: email.value,
      password: password.value,
      role: 'teacher'
    });
    router.push('/teacher/dashboard');
  } catch (error) {
    console.error('Signup failed:', error);
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold">Teacher Sign Up</h2>
        <p class="mt-2 text-gray-600">Create your account</p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleSignup">
        <div>
          <label for="name" class="form-label">Name</label>
          <input
            id="name"
            type="text"
            v-model="name"
            required
            class="form-input"
          />
        </div>

        <div>
          <label for="email" class="form-label">Email</label>
          <input
            id="email"
            type="email"
            v-model="email"
            required
            class="form-input"
          />
        </div>

        <div>
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            type="password"
            v-model="password"
            required
            class="form-input"
          />
        </div>

        <div>
          <button type="submit" class="w-full btn-primary">
            Sign up
          </button>
        </div>

        <div class="text-center">
          <p class="text-sm text-gray-600">
            Already have an account?
            <router-link to="/teacher/login" class="text-blue-500 hover:text-blue-600">
              Sign in
            </router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>