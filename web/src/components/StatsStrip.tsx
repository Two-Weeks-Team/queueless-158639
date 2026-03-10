"use client";
import { useEffect, useState } from 'react';
import { fetchQueue } from '@/lib/api';
import { ClockIcon, UsersIcon } from '@heroicons/react/24/outline';

export default function StatsStrip() {
  const [total, setTotal] = useState<number>(0);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const data = await fetchQueue();
        if (mounted) setTotal(data.queue_entries.length);
      } catch {}
    };
    load();
    const interval = setInterval(load, 10000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="flex gap-4 justify-center text-center py-4">
      <div className="flex items-center gap-2 bg-card px-4 py-2 rounded-md shadow-card border border-border">
        <UsersIcon className="h-5 w-5 text-primary" />
        <span>{total} waiting</span>
      </div>
      <div className="flex items-center gap-2 bg-card px-4 py-2 rounded-md shadow-card border border-border">
        <ClockIcon className="h-5 w-5 text-primary" />
        <span>Live updates</span>
      </div>
    </div>
  );
}
