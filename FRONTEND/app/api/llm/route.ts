import { NextResponse } from 'next/server';
import OpenAI from 'openai';

// DeepSeek is compatible with the OpenAI API format
const openai = new OpenAI({
  baseURL: 'https://api.deepseek.com',
  apiKey: process.env.DEEPSEEK_API || process.env.DEEPSEEK_API_KEY,
});

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { messages, model = 'deepseek-chat', temperature = 0.7 } = body;

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'A messages array is required' },
        { status: 400 }
      );
    }

    const completion = await openai.chat.completions.create({
      model,
      messages,
      temperature,
    });

    return NextResponse.json(completion.choices[0].message);
  } catch (error: any) {
    console.error('LLM API Error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal Server Error' },
      { status: 500 }
    );
  }
}
