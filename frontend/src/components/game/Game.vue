<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { gameApi } from '@/api/game';
import type { Problem, GameConfig, UserProgress } from '@/api/game';
import BalanceScale from './BalanceScale.vue';
import ProgressBar from './ProgressBar.vue';
import FeedbackMessage from './FeedbackMessage.vue';

const authStore = useAuthStore();
const config = ref<GameConfig | null>(null);
const currentProblem = ref<Problem | null>(null);
const userProgress = ref<UserProgress | null>(null);
const selectedOptions = ref<number[]>([]);
const tiltAngle = ref(0);
const feedback = ref({ message: '', type: 'info' as const, show: false });
const loading = ref(true);

const fetchGameConfig = async () => {
  try {
    config.value = await gameApi.getConfig();
  } catch (error) {
    console.error('Failed to fetch game config:', error);
    showFeedback('Failed to load game configuration', 'error');
  }
};

const fetchNewProblem = async () => {
  try {
    currentProblem.value = await gameApi.getProblem();
    selectedOptions.value = [];
    tiltAngle.value = 0;
  } catch (error) {
    console.error('Failed to fetch problem:', error);
    showFeedback('Failed to load new problem', 'error');
  }
};

const fetchUserProgress = async () => {
  if (!authStore.user?.id) return;
  
  try {
    userProgress.value = await gameApi.getUserProgress(authStore.user.id);
  } catch (error) {
    console.error('Failed to fetch user progress:', error);
  }
};

const showFeedback = (message: string, type: 'success' | 'error' | 'info') => {
  feedback.value = {
    message,
    type,
    show: true,
  };
};

const toggleOption = (option: number) => {
  const index = selectedOptions.value.indexOf(option);
  if (index === -1) {
    selectedOptions.value.push(option);
  } else {
    selectedOptions.value.splice(index, 1);
  }
};

const submitAnswer = async () => {
  if (!currentProblem.value || !authStore.user?.id) return;

  try {
    const response = await gameApi.submitAnswer(
      authStore.user.id,
      currentProblem.value.id,
      selectedOptions.value
    );

    tiltAngle.value = response.tiltAngle;
    showFeedback(response.feedback, response.correct ? 'success' : 'error');

    // Update progress
    await fetchUserProgress();

    // Load new problem after a delay
    setTimeout(fetchNewProblem, 2000);
  } catch (error) {
    console.error('Failed to submit answer:', error);
    showFeedback('Failed to submit answer', 'error');
  }
};

onMounted(async () => {
  await Promise.all([
    fetchGameConfig(),
    fetchUserProgress(),
    fetchNewProblem(),
  ]);
  loading.value = false;
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>

    <template v-else>
      <!-- Progress Section -->
      <div class="mb-8" v-if="userProgress">
        <ProgressBar
          :progress="userProgress.currentScore / (config?.levels[userProgress.currentLevel]?.requiredScore || 100)"
          :level="userProgress.currentLevel"
        />
        <div class="mt-2 text-sm text-gray-600">
          Streak: {{ userProgress.streak }} | Total Problems: {{ userProgress.totalProblems }}
        </div>
      </div>

      <!-- Game Section -->
      <div class="max-w-2xl mx-auto">
        <!-- Target Number -->
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold">Target Number</h2>
          <div class="text-4xl font-bold text-blue-600">
            {{ currentProblem?.targetNumber }}
          </div>
        </div>

        <!-- Balance Scale -->
        <BalanceScale :tilt-angle="tiltAngle">
          <template #left-pan>
            {{ currentProblem?.targetNumber }}
          </template>
          <template #right-pan>
            {{ selectedOptions.reduce((sum, n) => sum + n, 0) }}
          </template>
        </BalanceScale>

        <!-- Options -->
        <div class="mt-8 grid grid-cols-2 md:grid-cols-3 gap-4">
          <button
            v-for="option in currentProblem?.options"
            :key="option"
            @click="toggleOption(option)"
            class="p-4 text-xl rounded-lg transition-colors duration-200"
            :class="{
              'bg-blue-500 text-white': selectedOptions.includes(option),
              'bg-gray-200 hover:bg-gray-300': !selectedOptions.includes(option)
            }"
          >
            {{ option }}
          </button>
        </div>

        <!-- Submit Button -->
        <div class="mt-8 text-center">
          <button
            @click="submitAnswer"
            :disabled="selectedOptions.length === 0"
            class="px-8 py-3 bg-green-500 text-white rounded-lg text-lg font-semibold hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Submit Answer
          </button>
        </div>
      </div>

      <!-- Feedback Message -->
      <FeedbackMessage
        :message="feedback.message"
        :type="feedback.type"
        :show="feedback.show"
      />
    </template>
  </div>
</template>