import type { Metadata } from 'next';
import './globals.css';
import CyberGrid from '../components/CyberGrid';

export const metadata: Metadata = {
  title: 'SecAI - Cybersecurity Assistant',
  description: 'Advanced AI assistant tailored for security defense and CTF hints.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased relative min-h-screen" suppressHydrationWarning>
        {/* CRT Scanline Overlay */}
        <div 
          className="pointer-events-none fixed inset-0 z-[9999] opacity-[0.12] mix-blend-overlay"
          style={{
            background: 'linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06))',
            backgroundSize: '100% 2px, 3px 100%'
          }}
        />
        <CyberGrid />
        {children}
      </body>
    </html>
  );
}
