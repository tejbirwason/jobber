import React from 'react';
import { useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Briefcase, Clock, MapPin, Link as LinkIcon } from 'lucide-react';
import { Job } from '@/types/job';
import { useJobs } from '@/hooks/useJobs';

const JobDetails: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const { data: jobs = [] } = useJobs();

  const job = jobs.find((j: Job) => j.id === jobId);

  if (!job) return <div>Job not found</div>;
  return (
    <Card className='w-full'>
      {job.category_explanation && (
        <div className='bg-blue-100 p-4 mb-4 rounded-t-lg'>
          <p className='text-blue-800'>{job.category_explanation}</p>
        </div>
      )}
      <CardHeader>
        <CardTitle className='text-2xl font-bold'>{job.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className='space-y-4'>
          {job.link && (
            <div>
              <a href={job.link} target='_blank' rel='noopener noreferrer'>
                <Button>
                  <LinkIcon className='h-4 w-4 mr-2' />
                  Open Link
                </Button>
              </a>
            </div>
          )}
          <div className='flex items-center space-x-2'>
            <Briefcase className='h-5 w-5' />
            <span className='font-semibold'>{job.company}</span>
            {job.company_link && (
              <a
                href={job.company_link}
                target='_blank'
                rel='noopener noreferrer'
              >
                <LinkIcon className='h-4 w-4' />
              </a>
            )}
          </div>
          <div className='flex items-center space-x-2'>
            <MapPin className='h-5 w-5' />
            <span>{job.location}</span>
          </div>
          <div className='flex items-center space-x-2'>
            <Clock className='h-5 w-5' />
            <span>{new Date(job.timestamp).toLocaleDateString()}</span>
          </div>
          {job.employment_type && (
            <Badge variant='secondary'>{job.employment_type}</Badge>
          )}
          {job.description_html ? (
            <div>
              <h3 className='text-lg font-semibold mb-2'>Description</h3>
              <div className='max-h-96 overflow-y-auto'>
                <div
                  dangerouslySetInnerHTML={{ __html: job.description_html }}
                />
              </div>
            </div>
          ) : (
            job.description && (
              <div>
                <h3 className='text-lg font-semibold mb-2'>Description</h3>
                <div className='max-h-96 overflow-y-auto'>
                  <p>{job.description}</p>
                </div>
              </div>
            )
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default JobDetails;
