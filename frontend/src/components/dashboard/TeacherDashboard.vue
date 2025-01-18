<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { teacherApi } from '@/api/teacher';
import type { StudentData } from '@/api/teacher';

const students = ref<StudentData[]>([]);
const loading = ref(true);
const sortBy = ref<'level' | 'name'>('level');
const sortDirection = ref<'asc' | 'desc'>('desc');

const fetchStudents = async () => {
  try {
    students.value = await teacherApi.getStudents();
  } catch (error) {
    console.error('Failed to fetch students:', error);
  } finally {
    loading.value = false;
  }
};

const toggleSort = (field: 'level' | 'name') => {
  if (sortBy.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortBy.value = field;
    sortDirection.value = 'desc';
  }
};

const sortedStudents = computed(() => {
  return [...students.value].sort((a, b) => {
    const modifier = sortDirection.value === 'asc' ? 1 : -1;
    
    if (sortBy.value === 'level') {
      return (a.progress.currentLevel - b.progress.currentLevel) * modifier;
    } else {
      return a.name.localeCompare(b.name) * modifier;
    }
  });
});

onMounted(fetchStudents);
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">Student Progress Dashboard</h1>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>

      <!-- Student Data Table -->
      <div v-else class="bg-white rounded-lg shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th 
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="toggleSort('name')"
                >
                  <div class="flex items-center">
                    Student Name
                    <span v-if="sortBy === 'name'" class="ml-1">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th 
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="toggleSort('level')"
                >
                  <div class="flex items-center">
                    Current Level
                    <span v-if="sortBy === 'level'" class="ml-1">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  XP
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Accuracy
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="student in sortedStudents" :key="student.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div>
                      <div class="text-sm font-medium text-gray-900">
                        {{ student.name }}
                      </div>
                      <div class="text-sm text-gray-500">
                        {{ student.email }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">Level {{ student.progress.currentLevel }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ student.progress.currentScore }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ Math.round(student.accuracy * 100) }}%</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                    <div 
                      class="bg-blue-600 h-2.5 rounded-full" 
                      :style="{ width: `${Math.round(student.progress.currentScore / 100 * 100)}%` }"
                    ></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>