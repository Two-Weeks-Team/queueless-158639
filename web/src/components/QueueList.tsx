"use client";
import { useEffect, useState } from 'react';
import { fetchQueue, QueueEntry } from '@/lib/api';
import StatePanel from '@/components/StatePanel';
import clsx from 'clsx';

function QueueList() {
  const [entries, setEntries] = useState<QueueEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchQueue()
      .then((data) => {
        if (mounted) setEntries(data.queue_entries);
      })
      .catch((e) => {
        if (mounted) setError(e.message);
      });
    const interval = setInterval(() => {
      fetchQueue().then((data) => mounted && setEntries(data.queue_entries)).catch(() => {});
    }, 5000); // refresh every 5s
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  if (error) {
    return <StatePanel state="error" message={error} />;
  }

  if (entries === null) {
    return <StatePanel state="loading" />;
  }

  if (entries.length === 0) {
    return <StatePanel state="empty" message="The queue is currently empty." />;
  }

  return (
    <StatePanel state="success">
      <ul className="space-y-2">
        {entries.map((e) => (
          <li
            key={e.id}
            className={clsx(
              'p-3 rounded-lg border border-border bg-card flex justify-between items-center',
              'shadow-card'
            )}
          >
            <span>#{e.position} – Party of {e.party_size}</span>
            <span className={clsx({
              'text-success': e.status === 'called',
              'text-muted': e.status === 'pending',
            })}>
              {e.status}
            </span>
          </li>
        ))}
      </ul>
    </StatePanel>
  );
}

export default QueueList;
