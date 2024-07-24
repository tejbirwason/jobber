import React, { useState, useMemo } from 'react';
import { useNavigate, useParams, Outlet } from 'react-router-dom';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent } from '@/components/ui/card';
import { useQuery } from '@tanstack/react-query';

import JobListingItem from './JobListingItem';
import { fetchJobs } from '@/db';
import { Job } from '@/types/job';

const JobListingShell: React.FC = () => {
  const navigate = useNavigate();
  const { jobId } = useParams<{ jobId: string }>();
  const [selectedJobId, setSelectedJobId] = useState<string | null>(
    jobId || null
  );
  const [selectedCategory, setSelectedCategory] = useState('Ideal Match');

  const { data: jobs = [] } = useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  const sortedJobs = [...jobs].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const categories = [
    'Ideal Match',
    'Strong Potential',
    'Worth Considering',
    'Not Suitable',
  ];

  const jobsByCategory = useMemo(() => {
    return sortedJobs.reduce((acc, job) => {
      const category = job.category || 'Not Suitable';
      acc[category] = (acc[category] || []).concat(job);
      return acc;
    }, {} as Record<string, Job[]>);
  }, [sortedJobs]);

  const filteredJobs = jobsByCategory[selectedCategory] || [];

  const handleJobSelect = (id: string) => {
    setSelectedJobId(id);
    navigate(`/jobs/${id}`);
  };

  return (
    <div className='flex h-screen'>
      {/* Sidebar */}
      <div className='w-1/4 border-r flex flex-col'>
        <div className='p-4 border-b'>
          <div className='grid grid-cols-2 gap-2'>
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`p-2 text-xs rounded-md transition-colors ${
                  selectedCategory === category
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary hover:bg-secondary/80'
                }`}
              >
                {category}
                <br />({jobsByCategory[category]?.length || 0})
              </button>
            ))}
          </div>
        </div>
        <ScrollArea className='flex-grow'>
          {filteredJobs.map((job, index) => (
            <React.Fragment key={`${job.id}-${index}`}>
              <JobListingItem
                job={job}
                isSelected={job.id === selectedJobId}
                onSelect={handleJobSelect}
              />
              {index < filteredJobs.length - 1 && (
                <hr className='my-2 border-gray-200' />
              )}
            </React.Fragment>
          ))}
        </ScrollArea>
      </div>

      {/* Job Details */}
      <div className='w-3/4 p-4'>
        {selectedJobId ? (
          <Outlet />
        ) : (
          <Card>
            <CardContent className='pt-6'>
              <p className='text-center text-gray-500'>
                Select a job from the list to view details
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default JobListingShell;
