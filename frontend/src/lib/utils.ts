import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const getRelativeTime = (timestamp: string) => {
  const now = new Date();
  const jobDate = new Date(timestamp + 'Z');
  const localJobDate = new Date(jobDate.toLocaleString());
  const diffInSeconds = Math.floor(
    (now.getTime() - localJobDate.getTime()) / 1000
  );

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h`;
  return `${Math.floor(diffInSeconds / 86400)}d`;
};
