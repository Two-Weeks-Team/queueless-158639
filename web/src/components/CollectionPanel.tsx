"use client";
import { useEffect, useState } from 'react';
import { fetchQueue, QueueEntry } from '@/lib/api';
import StatePanel from '@/components/StatePanel';
import clsx from 'clsx';

function CollectionPanel() {
  const [history, setHistory] = useState<QueueEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    // For demo purposes we reuse queue data as "recent activity".
    fetchQueue()
      .then((data) => {
        if (mounted) setHistory(data.queue_entries.slice(-5).reverse());
      })
      .catch((e) => {
        if (mounted) setError(e.message);
      });
  }, []);

  if (error) {
    return <StatePanel state="error" message={error} />;
  }

  if (history === null) {
    return <StatePanel state="loading" />;
  }

  if (history.length === 0) {
    return <StatePanel state="empty" message="No recent activity yet." />;
  }

  return (
    <section className="mt-8">
      <h2 className="text-lg font-medium mb-3">Recent Activity</h2>
      <ul className="space-y-2">
        {history.map((e) => (
          <li
            key={e.id}
            className={clsx(
              'p-2 rounded-md bg-card border border-border shadow-card flex justify-between items-center'
            )}
          >
            <span>#{e.position} – Party of {e.party_size}</span>
            <span className="text-sm text-muted">{e.status}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default CollectionPanel;
