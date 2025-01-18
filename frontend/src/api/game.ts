import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

export interface GameConfig {
  minValue: number;
  maxValue: number;
  numOptions: number;
  timeLimit: number;
  visualFeedbackSensitivity: number;
  levels: {
    [key: number]: {
      requiredScore: number;
      targetRange: [number, number];
    };
  };
}

export interface Problem {
  id: string;
  targetNumber: number;
  options: number[];
}

export interface SubmitResponse {
  correct: boolean;
  feedback: string;
  tiltAngle: number;
  newStreak: number;
  newScore: number;
  newLevel: number;
}

export interface UserProgress {
  currentLevel: number;
  currentScore: number;
  streak: number;
  totalProblems: number;
}

export const gameApi = {
  async getConfig(): Promise<GameConfig> {
    const response = await axios.get(`${API_BASE_URL}/game/config`);
    return response.data;
  },

  async getProblem(): Promise<Problem> {
    const response = await axios.get(`${API_BASE_URL}/game/problem`);
    return response.data;
  },

  async submitAnswer(userId: string, problemId: string, selectedOptions: number[]): Promise<SubmitResponse> {
    const response = await axios.post(`${API_BASE_URL}/game/submit`, {
      userId,
      problemId,
      selectedOptions,
    });
    return response.data;
  },

  async getUserProgress(userId: string): Promise<UserProgress> {
    const response = await axios.get(`${API_BASE_URL}/user/${userId}/progress`);
    return response.data;
  },
};