import { Button } from '@/components/ui/button';
import { ExternalLink, ThumbsDown, ThumbsUp } from 'lucide-react';
import { Job } from '@/types/job';
import { updateJobCategory } from '@/db';
import { useToast } from '@/components/ui/use-toast';
import { getJobSource } from '@/lib/utils';

interface JobActionsProps {
  job: Job;
}

const JobActions = ({ job }: JobActionsProps) => {
  const { toast } = useToast();

  const jobSource = getJobSource(job.id);

  const handleInterested = async () => {
    try {
      await updateJobCategory(job.id, 'Interested');
      toast({
        title: 'Success',
        description: 'Job marked as Interested',
      });
    } catch (error) {
      console.error('Failed to update job category:', error);
      toast({
        title: 'Error',
        description: 'Failed to update job category',
        variant: 'destructive',
      });
    }
  };

  const handleNotInterested = async () => {
    try {
      await updateJobCategory(job.id, 'Not Interested');
      toast({
        title: 'Success',
        description: 'Job marked as Not Interested',
      });
    } catch (error) {
      console.error('Failed to update job category:', error);
      toast({
        title: 'Error',
        description: 'Failed to update job category',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className='flex space-x-2'>
      {job.link && (
        <a href={job.link} target='_blank' rel='noopener noreferrer'>
          <Button size='sm' variant='outline'>
            <ExternalLink className='h-4 w-4 mr-1' />
            {jobSource.name}
          </Button>
        </a>
      )}
      {job.company_link && (
        <a href={job.company_link} target='_blank' rel='noopener noreferrer'>
          <Button size='sm' variant='outline'>
            <ExternalLink className='h-4 w-4 mr-1' />
            {job.company}
          </Button>
        </a>
      )}
      <Button size='sm' variant='outline' onClick={handleNotInterested}>
        <ThumbsDown className='h-4 w-4' />
      </Button>
      <Button size='sm' variant='outline' onClick={handleInterested}>
        <ThumbsUp
          className={`h-4 w-4 mr-1 ${
            job.category === 'Interested' ? 'text-blue-400' : ''
          }`}
        />
        Interested
      </Button>
    </div>
  );
};

export default JobActions;
