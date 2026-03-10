"use client";
import Hero from '@/components/Hero';
import StatsStrip from '@/components/StatsStrip';
import InsightPanel from '@/components/InsightPanel';
import QueueList from '@/components/QueueList';
import CollectionPanel from '@/components/CollectionPanel';
import NotificationBell from '@/components/NotificationBell';

export default function HomePage() {
  return (
    <main className="container mx-auto p-4 space-y-8">
      <header className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-semibold">Queueless</h1>
        <NotificationBell />
      </header>
      <Hero />
      <StatsStrip />
      <InsightPanel />
      <section id="queue" className="space-y-4">
        <h2 className="text-xl font-medium">Current Queue</h2>
        <QueueList />
      </section>
      <CollectionPanel />
    </main>
  );
}
