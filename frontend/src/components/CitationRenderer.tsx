import React from 'react';
import { Link2 } from 'lucide-react';

export interface CitationSource {
  id: string;
  title: string;
  url?: string;
}

interface CitationRendererProps {
  sources: CitationSource[];
}

export default function CitationRenderer({ sources }: CitationRendererProps) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-dashed border-cyan-400/20">
      {sources.map((src, index) => (
        <a 
          key={`citation-${index}`}
          href={src.url || '#'} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-xs text-cyan-400 bg-cyan-400/5 border border-cyan-400/20 px-2.5 py-1 rounded-md no-underline transition-all duration-300 flex items-center gap-1 hover:bg-cyan-400/15 hover:border-cyan-400 hover:shadow-[0_0_10px_rgba(6,182,212,0.3)] hover:-translate-y-px"
          title={src.url}
        >
          <Link2 size={12} />
          {src.title}
        </a>
      ))}
    </div>
  );
}
