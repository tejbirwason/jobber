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

export interface JobSource {
  name: string;
  color: string;
}

export function getJobSource(jobId: string): JobSource {
  if (jobId.startsWith('dice_'))
    return { name: 'Dice', color: 'bg-green-100 text-green-800' };
  if (jobId.startsWith('indeed_'))
    return { name: 'Indeed', color: 'bg-blue-100 text-blue-800' };
  if (jobId.startsWith('yc_'))
    return { name: 'Y Combinator', color: 'bg-orange-100 text-orange-800' };
  if (jobId.startsWith('linkedin_'))
    return { name: 'LinkedIn', color: 'bg-sky-100 text-sky-800' };
  if (jobId.startsWith('glassdoor_'))
    return { name: 'Glassdoor', color: 'bg-emerald-100 text-emerald-800' };
  if (jobId.startsWith('zip_recruiter_'))
    return { name: 'ZipRecruiter', color: 'bg-purple-100 text-purple-800' };
  return { name: 'Unknown', color: 'bg-gray-100 text-gray-800' };
}

export function debounce<F extends (...args: any[]) => any>(
  func: F,
  waitFor: number
) {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<F>): void => {
    if (timeout !== null) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => func(...args), waitFor);
  };
}
