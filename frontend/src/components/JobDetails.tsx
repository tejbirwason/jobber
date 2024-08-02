import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Briefcase, Clock, MapPin, Calendar, ExternalLink } from 'lucide-react';
import { Job } from '@/types/job';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import JobSummary from '@/components/JobSummary';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { HelpCircle } from 'lucide-react';
import { Separator } from './ui/separator';

interface JobDetailsProps {
  job: Job | null;
  onClose: () => void;
}

const JobDetails = ({ job, onClose }: JobDetailsProps) => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    setIsOpen(!!job);
  }, [job]);

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) onClose();
  };

  if (!job) return null;

  const jobSource = (() => {
    if (job.id.startsWith('dice_'))
      return { name: 'Dice', color: 'bg-green-100 text-green-800' };
    if (job.id.startsWith('indeed_'))
      return { name: 'Indeed', color: 'bg-blue-100 text-blue-800' };
    if (job.id.startsWith('yc_'))
      return { name: 'Y Combinator', color: 'bg-orange-100 text-orange-800' };
    if (job.id.startsWith('linkedin_'))
      return { name: 'LinkedIn', color: 'bg-sky-100 text-sky-800' };
    if (job.id.startsWith('glassdoor_'))
      return { name: 'Glassdoor', color: 'bg-emerald-100 text-emerald-800' };
    if (job.id.startsWith('zip_recruiter_'))
      return { name: 'ZipRecruiter', color: 'bg-purple-100 text-purple-800' };
    return { name: 'Unknown', color: 'bg-gray-100 text-gray-800' };
  })();

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className='w-full max-w-5xl h-[80vh]' noAnimation>
        <Card className='w-full h-full overflow-auto'>
          <CardHeader className='pb-2'>
            <div className='flex justify-between items-start'>
              <div className='flex items-center'>
                <CardTitle className='text-xl font-bold'>{job.title}</CardTitle>
                <Badge variant='outline' className={`ml-2 ${jobSource.color}`}>
                  {jobSource.name}
                </Badge>
                {job.category_explanation && (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className='h-4 w-4 ml-2 text-gray-400' />
                      </TooltipTrigger>
                      <TooltipContent>
                        {Array.isArray(job.category_explanation) ? (
                          <ul className='list-disc pl-4'>
                            {job.category_explanation.map((reason, index) => (
                              <li key={index}>{reason}</li>
                            ))}
                          </ul>
                        ) : (
                          <p>{job.category_explanation}</p>
                        )}
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                )}
              </div>
              <div className='flex space-x-2'>
                {job.link && (
                  <a href={job.link} target='_blank' rel='noopener noreferrer'>
                    <Button size='sm' variant='outline'>
                      <ExternalLink className='h-4 w-4 mr-1' />
                      View Job
                    </Button>
                  </a>
                )}
                {job.company_link && (
                  <a
                    href={job.company_link}
                    target='_blank'
                    rel='noopener noreferrer'
                  >
                    <Button size='sm' variant='outline'>
                      <ExternalLink className='h-4 w-4 mr-1' />
                      View {job.company}
                    </Button>
                  </a>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className='space-y-4 text-sm'>
              <div className='grid grid-cols-2 gap-2'>
                <div className='flex items-center space-x-2'>
                  <Briefcase className='h-4 w-4' />
                  <span className='font-semibold'>{job.company}</span>
                </div>
                <div className='flex items-center space-x-2'>
                  <MapPin className='h-4 w-4' />
                  <span>{job.location}</span>
                </div>
                <div className='flex items-center space-x-2'>
                  <Calendar className='h-4 w-4' />
                  <span>
                    Posted: {new Date(job.date_posted).toLocaleDateString()}
                  </span>
                </div>
                <div className='flex items-center space-x-2'>
                  <Clock className='h-4 w-4' />
                  <span>
                    Updated: {new Date(job.timestamp).toLocaleDateString()}
                  </span>
                </div>
              </div>
              {job.employment_type && (
                <Badge variant='secondary' className='mt-1'>
                  {job.employment_type}
                </Badge>
              )}
              <Separator className='my-4' />
              <JobSummary job={job} />
              {(job.description_html || job.description_text) && (
                <div className='mt-6 pt-4 border-t border-gray-200 flex flex-col flex-grow'>
                  <h3 className='text-lg font-semibold mb-2'>Description</h3>
                  <div className='flex-grow overflow-y-auto text-sm'>
                    {job.description_html ? (
                      <div
                        dangerouslySetInnerHTML={{
                          __html: job.description_html,
                        }}
                      />
                    ) : (
                      <p>{job.description_text}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </DialogContent>
    </Dialog>
  );
};

export default JobDetails;
