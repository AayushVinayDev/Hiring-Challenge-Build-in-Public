import { collection, query, where, getDocs } from 'firebase/firestore';
import { db } from '../firebase';
import type { UserProgress } from './game';

export interface StudentData {
  id: string;
  name: string;
  email: string;
  progress: UserProgress;
  accuracy: number;
}

export const teacherApi = {
  async getStudents(): Promise<StudentData[]> {
    const studentsRef = collection(db, 'users');
    const q = query(studentsRef, where('role', '==', 'student'));
    const snapshot = await getDocs(q);
    
    return snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
    })) as StudentData[];
  }
};