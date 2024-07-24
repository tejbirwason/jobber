import { useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchJobs } from '@/db';
import { Job } from '@/types/job';

export const useJobs = () => {
  const queryClient = useQueryClient();

  const query = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
  });

  const markJobAsSeen = (jobId: string) => {
    queryClient.setQueryData(['jobs'], (oldData: Job[] | undefined) => {
      if (!oldData) return oldData;
      return oldData.map((job) =>
        job.id === jobId ? { ...job, seen: true } : job
      );
    });
  };

  return { ...query, markJobAsSeen };
};
