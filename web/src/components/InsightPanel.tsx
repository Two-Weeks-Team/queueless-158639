"use client";
import { useEffect, useState } from 'react';
import { fetchWaitTime } from '@/lib/api';
import StatePanel from '@/components/StatePanel';

export default function InsightPanel() {
  const [waitTime, setWaitTime] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const data = await fetchWaitTime();
        if (mounted) setWaitTime(data.wait_time);
      } catch (e: any) {
        if (mounted) setError(e.message);
      }
    };
    load();
    const interval = setInterval(load, 15000); // refresh every 15s
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  if (error) {
    return <StatePanel state="error" message={error} />;
  }

  if (waitTime === null) {
    return <StatePanel state="loading" />;
  }

  return (
    <StatePanel state="success">
      <div className="text-center text-2xl font-medium">
        Estimated Wait Time: <span className="text-primary">{waitTime} min</span>
      </div>
    </StatePanel>
  );
}
