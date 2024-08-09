import React, { useState, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
} from 'react-beautiful-dnd';
import { Loader2 } from 'lucide-react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

import JobListingItem from './JobListingItem';
import { Job } from '@/types/job';
import { fetchJobs, updateJobCategory } from '@/db';
import JobDetails from './JobDetails';
import { debounce } from '@/lib/utils';

const JobListingShell: React.FC = () => {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const {
    data: jobs = [],
    refetch,
    isLoading,
  } = useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    refetchInterval: 5 * 60 * 1000,
  });

  const sortedJobs = useMemo(
    () =>
      [...jobs].sort(
        (a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      ),
    [jobs]
  );

  const handleJobSelect = useCallback((job: Job) => {
    setSelectedJob(job);
  }, []);

  const handleCloseModal = useCallback(() => {
    setSelectedJob(null);
  }, []);

  const categories = [
    // 'Not Interested',
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

  const debouncedUpdateJobCategory = useCallback(
    debounce(async (jobId: string, newCategory: string) => {
      try {
        await updateJobCategory(jobId, newCategory);
        refetch();
      } catch (error) {
        console.error('Failed to update job category:', error);
      }
    }, 500),
    [refetch]
  );

  const onDragEnd = useCallback(
    (result: DropResult) => {
      const { destination, source, draggableId } = result;

      if (
        !destination ||
        (destination.droppableId === source.droppableId &&
          destination.index === source.index)
      ) {
        return;
      }

      const job = sortedJobs.find((j) => j.id === draggableId);
      if (!job) return;

      const newCategory = destination.droppableId;
      debouncedUpdateJobCategory(job.id, newCategory);
    },
    [sortedJobs, debouncedUpdateJobCategory]
  );

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-screen'>
        <Loader2 className='w-8 h-8 animate-spin' />
      </div>
    );
  }

  const renderJob = ({
    index,
    style,
    data: category,
  }: {
    index: number;
    style: React.CSSProperties;
    data: string;
  }) => {
    const job = jobsByCategory[category][index];
    return (
      <Draggable key={job.id} draggableId={job.id} index={index}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            style={{ ...style, ...provided.draggableProps.style }}
            className={`mb-2 ${snapshot.isDragging ? 'opacity-50' : ''}`}
          >
            <JobListingItem
              job={job}
              isSelected={job.id === selectedJob?.id}
              onSelect={() => handleJobSelect(job)}
            />
          </div>
        )}
      </Draggable>
    );
  };

  return (
    <div className='flex h-screen'>
      <DragDropContext onDragEnd={onDragEnd}>
        <div className='flex'>
          {categories.map((category) => {
            const categoryJobs = jobsByCategory[category] || [];
            const unseenJobs = categoryJobs.filter((job) => !job.seen).length;
            return (
              <div
                key={category}
                className='flex-shrink-0 w-80 min-w-[20rem] p-2'
              >
                <h2 className='font-bold mb-2'>
                  {category} ({unseenJobs})
                </h2>
                <Droppable droppableId={category}>
                  {(provided) => (
                    <div
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      className='p-2 rounded min-h-[200px] h-[calc(100vh-100px)]'
                    >
                      <AutoSizer disableHeight>
                        {({ width }) => (
                          <List
                            height={window.innerHeight - 100}
                            itemCount={categoryJobs.length}
                            itemSize={100}
                            width={width}
                            itemData={category}
                          >
                            {renderJob}
                          </List>
                        )}
                      </AutoSizer>
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
