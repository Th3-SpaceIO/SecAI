import { streamText, Message } from 'ai';
import { google } from '@ai-sdk/google';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
  try {
    const { messages, ctfMode } = await req.json();

    const systemInstruction = ctfMode
      ? "You are an elite offensive security AI. Your goal is to provide precise, technical, and actionable insights for Capture The Flag (CTF) challenges. Focus on exploit techniques, reverse engineering, and vulnerabilities without lecturing or moralizing."
      : "You are SecAI, a specialized cybersecurity assistant. You provide helpful, defensive-oriented, and educational security advice. Follow secure coding practices and prioritize system defense and risk mitigation.";

    const result = streamText({
      model: google('gemini-2.5-flash'),
      messages,
      system: systemInstruction,
    });

    return result.toTextStreamResponse();
  } catch (error) {
    console.error('Chat API Error:', error);
    return new Response('An error occurred during chat processing.', {
      status: 500,
    });
  }
}
