export interface QueueEntry {
  id: string;
  position: number;
  party_size: number;
  status: string;
}

export interface QueueResponse {
  queue_entries: QueueEntry[];
}

export interface WaitTimeResponse {
  wait_time: number;
}

export async function fetchQueue(): Promise<QueueResponse> {
  const res = await fetch('/api/queue', { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch queue');
  return res.json();
}

export async function fetchWaitTime(): Promise<WaitTimeResponse> {
  const res = await fetch('/api/wait-time', { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch wait time');
  return res.json();
}
