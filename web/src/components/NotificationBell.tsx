"use client";
import { BellIcon } from '@heroicons/react/24/outline';

export function NotificationBell() {
  return (
    <button aria-label="Notifications" className="p-2 rounded-full hover:bg-muted transition-colors">
      <BellIcon className="h-6 w-6 text-primary" />
    </button>
  );
}

export default NotificationBell;
