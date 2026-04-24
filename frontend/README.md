# SecAI - Frontend Desktop Interface

![SecAI UI Overview](https://img.shields.io/badge/Status-Active-brightgreen)
![Next.js](https://img.shields.io/badge/Next.js-15.1.7-black?logo=next.js)
![React](https://img.shields.io/badge/React-19.0-blue?logo=react)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?logo=tailwind-css)

Welcome to the frontend application for **SecAI**, an elite cybersecurity AI assistant and Capture The Flag (CTF) offensive analysis engine. This UI is built specifically to provide a high-fidelity, cyber-themed responsive interface to interact seamlessly with Google's Gemini LLMs over custom robust data streams.

[View the Complete SecAI Repository Here](https://github.com/thespaceio/Sec-AI)

---

## Core Features

- **Cyber-Aesthetic UI:** A fully custom terminal-style interface complete with glassmorphic hardware panels, moving CRT scanlines (`CyberGrid`), and chamfered edges.
- **Hardware-Accelerated Animations:** Smooth micro-animations and component transitions powered by `framer-motion`.
- **Dual Operating Modes:** Toggle between defensive monitoring mode and an aggressive CTF offensive exploitation mode inside the chat ecosystem.
- **Custom Streaming Engine:** Bypasses standard Vercel AI SDK parser fragility with a built-in pure JavaScript `TextDecoder` that guarantees immediate byte-by-byte markdown visualization without lock-ups.
- **Dynamic Syntax Highlighting:** Integrated citations, tool-call tracking, and markdown rendering using standard plugin ecosystems.

---

## Getting Started

### Prerequisites
Make sure you have Node.js and NPM installed on your machine.

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the necessary dependencies:
   ```bash
   npm install
   ```

### Environment Variables

You must configure your API keys locally before the backend engine will process chat streams. Create a file named `.env.local` in the root of the `frontend` folder and add the following:

```env
GOOGLE_GENERATIVE_AI_API_KEY=your_gemini_api_key_here
```
*(Note: `.env.local` is intentionally ignored by source control to prevent accidental leaks. Do not commit this file.)*

### Running the Dev Server

Spin up the local development instance on port 3000:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

---

## Architecture Details

- **`src/app/api/chat/route.ts`**: The Next.js API route that bootstraps Google's `gemini-2.5-flash` model and initiates the plaintext byte stream (`.toTextStreamResponse()`).
- **`src/components/ChatInterface.tsx`**: The main presentation layer that manages the chat log mapping, input states, and UI controls.
- **`src/hooks/useChat.ts`**: A robust, standalone React hook that consumes the backend stream manually, bypassing Vercel SDK version mismatches for flawless, unbroken streaming.

---

## Security Practices

Given the nature of SecAI, the frontend is built entirely statically. All LLM inferences and external requests are tightly proxy-routed through the Next.js boundary (`/api/chat`). Your API keys do not leak externally to the browser scope.
