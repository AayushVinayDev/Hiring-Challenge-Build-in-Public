import { defineStore } from 'pinia';
import { auth } from '../firebase';
import { 
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut
} from 'firebase/auth';

interface UserData {
  name: string;
  email: string;
  password: string;
  age?: number;
  role: 'student' | 'teacher';
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as any,
    loading: false,
    error: null as string | null,
  }),
  
  actions: {
    async signup(userData: UserData) {
      try {
        this.loading = true;
        this.error = null;
        const { user } = await createUserWithEmailAndPassword(
          auth,
          userData.email,
          userData.password
        );
        // Here you would typically save additional user data to your backend
        this.user = user;
      } catch (error: any) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async login(email: string, password: string) {
      try {
        this.loading = true;
        this.error = null;
        const { user } = await signInWithEmailAndPassword(auth, email, password);
        this.user = user;
      } catch (error: any) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        await signOut(auth);
        this.user = null;
      } catch (error: any) {
        this.error = error.message;
        throw error;
      }
    }
  }
});