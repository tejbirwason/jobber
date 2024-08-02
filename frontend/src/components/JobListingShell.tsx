import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
} from 'react-beautiful-dnd';
import { Loader2 } from 'lucide-react';

import JobListingItem from './JobListingItem';
import { Job } from '@/types/job';
import { fetchJobs, updateJobCategory } from '@/db';
import JobDetails from './JobDetails';

const JobListingShell: React.FC = () => {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const {
    data: jobs = [],
    refetch,
    isLoading,
  } = useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  const sortedJobs = [...jobs].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const handleJobSelect = (job: Job) => {
    setSelectedJob(job);
  };

  const handleCloseModal = () => {
    setSelectedJob(null);
  };

  const categories = [
    'Not Suitable',
    'Worth Considering',
    'Strong Potential',
    'Ideal Match',
    'Interested',
    'Applied',
  ];

  const jobsByCategory = useMemo(() => {
    return sortedJobs.reduce((acc, job) => {
      const category = job.category || 'Not Suitable';
      acc[category] = (acc[category] || []).concat(job);
      return acc;
    }, {} as Record<string, Job[]>);
  }, [sortedJobs]);

  const onDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;

    if (!destination) {
      return;
    }

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const job = sortedJobs.find((j) => j.id === draggableId);
    if (!job) return;

    const newCategory = destination.droppableId;

    try {
      await updateJobCategory(job.id, newCategory);
      refetch();
    } catch (error) {
      console.error('Failed to update job category:', error);
    }
  };

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-screen'>
        <Loader2 className='w-8 h-8 animate-spin' />
      </div>
    );
  }
  // TODO: Drag and drop not working

  return (
    <div className='flex h-screen'>
      <DragDropContext onDragEnd={onDragEnd}>
        <div className='flex-grow flex overflow-x-auto'>
          {categories.map((category) => {
            const categoryJobs = jobsByCategory[category] || [];
            const unseenJobs = categoryJobs.filter((job) => !job.seen).length;
            return (
              <div key={category} className='flex-shrink-0 w-64 p-2'>
                <h2 className='font-bold mb-2'>
                  {category} ({unseenJobs})
                </h2>
                <Droppable droppableId={category}>
                  {(provided) => (
                    <div
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      className='bg-gray-100 p-2 rounded min-h-[200px]'
                    >
                      {categoryJobs.map((job, index) => (
                        <Draggable
                          key={job.id}
                          draggableId={job.id}
                          index={index}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`mb-2 ${
                                snapshot.isDragging ? 'opacity-50' : ''
                              }`}
                            >
                              <JobListingItem
                                job={job}
                                isSelected={job.id === selectedJob?.id}
                                onSelect={() => handleJobSelect(job)}
                              />
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            );
          })}
        </div>
      </DragDropContext>

      <JobDetails job={selectedJob} onClose={handleCloseModal} />
    </div>
  );
};

export default JobListingShell;
