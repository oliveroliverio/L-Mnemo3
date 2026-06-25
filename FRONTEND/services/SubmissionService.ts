import { ArtifactPayload } from '../types';

const API_URL = process.env.NEXT_PUBLIC_SQLITE_API || 'http://localhost:3002';

export class SubmissionService {
  static async submitArtifact(payload: ArtifactPayload): Promise<void> {
    try {
      const response = await fetch(`${API_URL}/ingest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Submission failed');
      }
    } catch (error) {
      console.error('SubmissionService:', error);
      throw error;
    }
  }
}
