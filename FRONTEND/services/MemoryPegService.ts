import { MemoryPegMetadata } from '../types';

const API_URL = process.env.NEXT_PUBLIC_MEMORY_PEG_API || 'http://localhost:3001';

export class MemoryPegService {
  static async getCharacters(): Promise<MemoryPegMetadata> {
    try {
      // In a real scenario, this would be an actual API call.
      // If the API isn't built yet, we could mock this.
      // We will attempt to fetch, and if it fails, throw an error to be handled by react-query
      const response = await fetch(`${API_URL}/getCharacters`);
      if (!response.ok) {
        throw new Error('Failed to fetch Memory Peg data');
      }
      return await response.json();
    } catch (error) {
      console.error('MemoryPegService:', error);
      throw error;
    }
  }
}
