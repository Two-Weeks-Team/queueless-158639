"use client";
import { useRef } from 'react';
import { scrollTo } from '@/lib/utils';

export default function Hero() {
  const btnRef = useRef<HTMLButtonElement>(null);
  const handleJoin = () => {
    // In a real app this would open the QR scanner or post a join request.
    // For the demo we simply scroll to the queue list.
    const el = document.getElementById('queue');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="text-center py-12 space-y-6 animate-fade-in">
      <h1 className="text-4xl font-bold text-primary">{"Transform wait times into seamless experiences."}</h1>
      <p className="text-lg text-foreground max-w-xl mx-auto">
        Scan a QR code, join the virtual line, and watch your position update in real‑time. No more staring at a crowded lobby.
      </p>
      <button
        ref={btnRef}
        onClick={handleJoin}
        className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-accent transition-colors"
      >
        Join the Queue
      </button>
    </section>
  );
}
