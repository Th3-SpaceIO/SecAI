'use client';

import React, { useRef, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChat } from '../hooks/useChat';
import CitationRenderer from './CitationRenderer';
import { Send, Shield, Terminal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Decryption Cipher Hook/Component
const ScrambleText = ({ text }: { text: string }) => {
  const [displayChars, setDisplayChars] = useState<string[]>([]);
  const iterationRef = useRef(0);

  useEffect(() => {
    const chars = '01XY!@#$%^&*<>[]{}ZYXWVUTSRQP';
    iterationRef.current = 0;
    
    // Ensure that setting the interval doesn't skip initial frames
    setDisplayChars(chars.substring(0, text.length).split(''));

    const interval = setInterval(() => {
      setDisplayChars(
        text.split('').map((letter, index) => {
          if (index < iterationRef.current) {
            return text[index];
          }
          if (letter === ' ') return ' ';
          return chars[Math.floor(Math.random() * chars.length)];
        })
      );
      
      if (iterationRef.current >= text.length) {
        clearInterval(interval);
      }
      
      iterationRef.current += 1 / 3; // Tune decryption speed (approx 1.5s total)
    }, 40);
    
    return () => clearInterval(interval);
  }, [text]);

  return (
    <span>
      {displayChars.map((char, index) => (
        <span key={`char-${index}`}>{char}</span>
      ))}
    </span>
  );
};

export default function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit, ctfMode, toggleCtfMode, isLoading } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const extractVirtualCitations = (content: string) => {
    const citations = [];
    if (content.toLowerCase().includes('cve-')) {
      citations.push({ id: 'cve', title: 'NVD Database Search', url: 'https://nvd.nist.gov/vuln/search' });
    }
    if (content.toLowerCase().includes('owasp')) {
      citations.push({ id: 'owasp', title: 'OWASP Top 10', url: 'https://owasp.org/www-project-top-ten/' });
    }
    return citations;
  };

  return (
    <div className="flex flex-col h-screen w-full bg-slate-900 text-slate-50 font-sans overflow-hidden">
      
      {/* Glassmorphic Header */}
      <header className="flex justify-between items-center px-6 py-4 bg-slate-950/70 backdrop-blur-md border-b border-cyan-400/20 shadow-lg z-20">
        <div className="flex items-center gap-2 text-xl font-bold text-cyan-400 glitch-text">
          <Shield size={26} strokeWidth={2.5} />
          <span>Sec<span className="text-slate-200 drop-shadow-none">AI</span></span>
        </div>
        
        <div className="flex items-center gap-3 text-sm font-medium transition-colors duration-300">
          <span className={ctfMode ? "text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]" : "text-slate-400"}>
            {ctfMode ? 'CTF Hint Mode' : 'Defense Mode'}
          </span>
          <label className="relative inline-block w-11 h-6 cursor-pointer">
            <input 
              type="checkbox" 
              checked={ctfMode} 
              onChange={toggleCtfMode} 
              className="peer sr-only"
              aria-label="Toggle CTF Mode"
            />
            <div className="w-11 h-6 bg-slate-700 rounded-full border border-white/5 peer-checked:bg-red-500/20 peer-checked:border-red-500 transition-colors duration-300 after:content-[''] after:absolute after:top-[2px] after:left-[3px] after:bg-slate-50 after:border-gray-300 after:border after:rounded-full after:h-[18px] after:w-[18px] after:transition-all peer-checked:after:translate-x-[18px] peer-checked:after:bg-red-500 peer-checked:after:border-transparent peer-checked:after:shadow-[0_0_10px_rgba(239,68,68,0.8)] shadow-inner"></div>
          </label>
        </div>
      </header>

      {/* Main Central Area - Holds both Empty State Background and Messages */}
      <div className="flex-1 relative overflow-y-auto p-8 flex flex-col gap-6 scroll-smooth scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700 hover:scrollbar-thumb-slate-600 z-10">
        
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div 
              key="empty-state"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.3 } }}
              className="absolute inset-0 flex flex-col items-center justify-center text-center z-0 overflow-hidden"
            >
              {/* Perspective Grid Background */}
              <div className="absolute inset-0 top-1/4 perspective-grid pointer-events-none opacity-40 mix-blend-screen" />

              {/* Network Radar Sweep */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.35]">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 6, ease: 'linear', repeat: Infinity }}
                  className="w-[900px] h-[900px] rounded-full mix-blend-screen"
                  style={{
                    background: 'conic-gradient(from 90deg at 50% 50%, rgba(6,182,212,0) 0%, rgba(6,182,212,0.1) 50%, rgba(6,182,212,0) 100%)',
                  }}
                />
                <div className="absolute w-[350px] h-[350px] border border-cyan-400/20 rounded-full" />
                <div className="absolute w-[600px] h-[600px] border border-cyan-400/10 rounded-full" />
                <div className="absolute w-full h-[1px] bg-cyan-400/10" />
                <div className="absolute h-full w-[1px] bg-cyan-400/10" />
              </div>

              {/* Central Terminal Identity Prompt */}
              <div className="relative z-10 flex flex-col items-center mt-[-10vh]">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", bounce: 0.4, duration: 1 }}
                >
                  <Terminal size={64} strokeWidth={1} className="text-cyan-400/80 mb-6 drop-shadow-[0_0_20px_rgba(6,182,212,0.5)]" />
                </motion.div>
                
                <h2 className="text-cyan-400 text-xl font-mono tracking-[0.25em] font-medium drop-shadow-[0_0_10px_rgba(6,182,212,0.6)]">
                  <ScrambleText text="SYSTEM INITIALIZED" />
                </h2>
                
                <motion.p 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.5, duration: 0.8 }}
                  className="mt-5 text-slate-400 font-mono text-sm max-w-[280px] leading-relaxed border-t border-cyan-400/20 pt-4"
                >
                  Secure communications channel established. Proxy bypassed. Awaiting directive.
                </motion.p>
              </div>
            </motion.div>
          )}

          {/* Chat Bubbles */}
          <motion.div 
            key="message-list"
            className="relative z-10 flex flex-col gap-6 w-full max-w-4xl mx-auto"
          >
            {messages.map((m, index) => (
              <motion.div 
                key={`msg-${index}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: [0.2, 0.8, 0.2, 1] }}
                className={`relative overflow-hidden max-w-[85%] p-5 leading-relaxed text-[0.95rem] border border-cyan-400/20 ${
                  m.role === 'user' 
                    ? 'self-end bg-cyan-400/10 text-slate-200 shadow-[0_4px_25px_rgba(6,182,212,0.05)] drop-shadow-[0_0_8px_rgba(6,182,212,0.1)]' 
                    : 'self-start bg-slate-800 text-slate-300 shadow-[0_8px_30px_rgba(0,0,0,0.4)]'
                }`}
                style={{
                  clipPath: 'polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px)'
                }}
              >
                <motion.div
                  initial={{ top: 0, opacity: 1 }}
                  animate={{ top: "100%", opacity: 0 }}
                  transition={{ duration: 0.6, ease: "linear" }}
                  className="absolute left-0 right-0 h-[2px] bg-cyan-400 shadow-[0_0_10px_rgba(6,182,212,1)] z-20 pointer-events-none"
                />
                {m.role === 'user' ? (
                  m.content
                ) : (
                  <div className="markdown-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {m.content}
                    </ReactMarkdown>
                    
                    <CitationRenderer sources={extractVirtualCitations(m.content)} />
                  </div>
                )}
              </motion.div>
            ))}
            
            {/* Neural Processing Waveform */}
            <AnimatePresence>
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="self-start flex items-center gap-3 p-4 bg-slate-800/80 text-cyan-500 text-[0.8rem] font-mono tracking-widest uppercase border-l-2 border-cyan-500 shadow-[0_8px_30px_rgba(0,0,0,0.4)]"
                  style={{ clipPath: 'polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px)' }}
                >
                  <span className="opacity-80 drop-shadow-[0_0_5px_rgba(6,182,212,0.8)]">PROCESSING_</span>
                  <div className="flex items-end gap-[3px] h-4">
                    {[0, 1, 2, 3].map((i) => (
                      <motion.div
                        key={`wave-${i}`}
                        animate={{ height: ['20%', '100%', '20%'] }}
                        transition={{ 
                          repeat: Infinity, 
                          duration: 0.6, 
                          delay: i * 0.15,
                          ease: "easeInOut"
                        }}
                        className="w-1 bg-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,1)]"
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div ref={messagesEndRef} />
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Glassmorphic Sticky Input Form */}
      <div className="p-6 bg-slate-950/70 backdrop-blur-md border-t border-cyan-400/10 shadow-[0_-4px_30px_rgba(0,0,0,0.4)] sticky bottom-0 z-20">
        <form onSubmit={handleSubmit} className="flex gap-4 max-w-5xl mx-auto">
          <input
            className="flex-1 bg-slate-900/80 border-l-[3px] border-l-cyan-500/50 border-y border-r border-slate-700 text-slate-50 px-5 py-4 text-base outline-none transition-all duration-300 focus:border-cyan-400 focus:bg-slate-900 focus-within:shadow-[0_0_20px_rgba(6,182,212,0.4)]"
            style={{ clipPath: 'polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px)' }}
            value={input || ''}
            placeholder={ctfMode ? "Initialize attack vector query..." : "Define security incident details..."}
            onChange={handleInputChange}
            autoComplete="off"
            autoFocus
          />
          <button 
            type="submit" 
            disabled={!input || input.trim().length === 0 || isLoading}
            className="bg-cyan-400/10 text-cyan-400 border border-cyan-400/30 px-6 font-semibold flex items-center gap-2 transition-all duration-300 hover:not(:disabled):bg-cyan-400/20 hover:not(:disabled):border-cyan-400 hover:not(:disabled):shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:not(:disabled):-translate-y-0.5 disabled:opacity-40 disabled:cursor-not-allowed disabled:border-transparent"
            style={{ clipPath: 'polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px)' }}
          >
            <Send size={18} />
            <span>Transmit</span>
          </button>
        </form>
      </div>
    </div>
  );
}
