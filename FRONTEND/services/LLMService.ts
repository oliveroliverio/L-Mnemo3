export class LLMService {
  static async chat(messages: { role: string; content: string }[], model = 'deepseek-chat') {
    try {
      const response = await fetch('/api/llm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages, model }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || 'Failed to fetch from LLM API');
      }

      return await response.json();
    } catch (error) {
      console.error('LLMService:', error);
      throw error;
    }
  }
}
