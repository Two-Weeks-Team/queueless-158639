"use client";
import { memo } from 'react';
import clsx from 'clsx';

interface Props {
  state: 'loading' | 'empty' | 'error' | 'success';
  message?: string;
  children?: React.ReactNode;
}

const stateClasses = {
  loading: 'text-primary',
  empty: 'text-muted',
  error: 'text-warning',
  success: 'text-success',
};

function StatePanel({ state, message, children }: Props) {
  const base = 'p-4 rounded-md border border-border bg-card animate-fade-in';
  const content = (
    <div className={clsx(base, stateClasses[state])}>
      {state === 'loading' && <p>Loading…</p>}
      {state === 'empty' && <p>{message ?? 'No data available.'}</p>}
      {state === 'error' && <p>{message ?? 'Something went wrong.'}</p>}
      {state === 'success' && children}
    </div>
  );
  return content;
}

export default memo(StatePanel);
