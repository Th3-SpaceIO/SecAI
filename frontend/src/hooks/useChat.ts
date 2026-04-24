'use client';

import { useState, useCallback } from 'react';
import { Message } from 'ai';

export function useChat() {
  const [ctfMode, setCtfMode] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const toggleCtfMode = useCallback(() => {
    setCtfMode((prev) => !prev);
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setInput(e.target.value);
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: input };
    // Optimistic UI update
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMessage], ctfMode })
      });

      if (!res.ok) throw new Error(res.statusText);

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      
      const assistantMessageId = (Date.now() + 1).toString();
      setMessages((prev) => [...prev, { id: assistantMessageId, role: 'assistant', content: '' }]);

      let currentResponse = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          currentResponse += decoder.decode(value, { stream: true });
          
          setMessages((prev) => prev.map(msg => 
            msg.id === assistantMessageId ? { ...msg, content: currentResponse } : msg
          ));
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [input, messages, isLoading, ctfMode]);

  return {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    ctfMode,
    toggleCtfMode,
  };
}