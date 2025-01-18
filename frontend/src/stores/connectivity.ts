import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export interface LocalProgress {
  level: number;
  xp: number;
  questionsCorrect: number;
  questionsAttempted: number;
  timestamp: number;
}

const STORAGE_KEY = 'balance_game_progress';

export const useConnectivityStore = defineStore('connectivity', () => {
  const isOnline = ref(navigator.onLine);
  const isSyncing = ref(false);
  const lastSyncTime = ref<number | null>(null);

  // Watch online status
  window.addEventListener('online', () => {
    isOnline.value = true;
    syncProgress();
  });
  window.addEventListener('offline', () => {
    isOnline.value = false;
  });

  function saveLocalProgress(progress: LocalProgress) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
    } catch (error) {
      console.error('Failed to save progress locally:', error);
    }
  }

  function getLocalProgress(): LocalProgress | null {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Failed to retrieve local progress:', error);
      return null;
    }
  }

  function clearLocalProgress() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear local progress:', error);
    }
  }

  async function syncProgress() {
    if (!isOnline.value || isSyncing.value) return;

    const localProgress = getLocalProgress();
    if (!localProgress) return;

    try {
      isSyncing.value = true;
      
      // Send local progress to backend
      const response = await fetch('/api/game/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(localProgress),
      });

      if (!response.ok) throw new Error('Sync failed');

      const serverData = await response.json();
      
      // Clear local progress after successful sync
      clearLocalProgress();
      lastSyncTime.value = Date.now();

      return serverData;
    } catch (error) {
      console.error('Failed to sync progress:', error);
      throw error;
    } finally {
      isSyncing.value = false;
    }
  }

  return {
    isOnline,
    isSyncing,
    lastSyncTime,
    saveLocalProgress,
    getLocalProgress,
    clearLocalProgress,
    syncProgress,
  };
});