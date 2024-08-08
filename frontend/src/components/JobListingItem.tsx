import React, { useState } from 'react';
import { ArrowUpRight, Briefcase, Circle } from 'lucide-react';
import { Job } from '@/types/job';
import { useJobs } from '@/hooks/useJobs';
import { updateJobSeen } from '@/db';

interface JobListingItemProps {
  job: Job;
  isSelected: boolean;
  onSelect: () => void;
}

const JobListingItem: React.FC<JobListingItemProps> = ({
  job,
  isSelected,
  onSelect,
}) => {
  const { markJobAsSeen } = useJobs();
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = async (e: React.MouseEvent) => {
    // Prevent click during drag
    if (e.defaultPrevented) return;

    onSelect();
    markJobAsSeen(job.id);

    try {
      await updateJobSeen(job.id);
    } catch (error) {
      console.error('Error updating job seen status:', error);
    }
  };

  const handleLinkClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(job.link, '_blank');
  };

  return (
    <div
      className={`p-3 bg-gray-50 rounded-lg shadow-md cursor-pointer relative ${
        isSelected ? 'ring-2 ring-primary' : ''
      } ${isHovered ? 'ring-2 ring-blue-300' : ''}`}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {!job.seen && (
        <Circle className='h-2 w-2 absolute top-2 right-2 text-blue-500 fill-current' />
      )}
      <div className='flex flex-col space-y-1'>
        <div className='font-semibold text-sm text-primary break-words'>
          {job.title}
        </div>
        <div className='text-xs text-gray-500 flex items-center'>
          <Briefcase className='h-3 w-3 mr-1 text-gray-400 flex-shrink-0' />
          <span className='break-words'>{job.company}</span>
        </div>
      </div>
      {isHovered && (
        <button
          className='absolute top-2 right-2 p-1 bg-white rounded shadow-md'
          onClick={handleLinkClick}
        >
          <ArrowUpRight className='h-4 w-4' />
        </button>
      )}
    </div>
  );
};

export default JobListingItem;
