import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Outlet } from 'react-router-dom';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Briefcase, Clock } from 'lucide-react';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, ScanCommand } from '@aws-sdk/lib-dynamodb';

interface Job {
  website_jobid: string;
  timestamp: string;
  company: string;
  date_posted: string;
  link: string;
  location: string;
  title: string;
}

const JobListingPage: React.FC = () => {
  const navigate = useNavigate();
  const { jobId } = useParams<{ jobId: string }>();
  const [selectedJobId, setSelectedJobId] = useState<string | null>(
    jobId || null
  );
  const [jobListings, setJobListings] = useState<Job[]>([]);

  useEffect(() => {
    const fetchJobs = async () => {
      const client = new DynamoDBClient({
        region: 'us-east-1',
        credentials: {
          accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY_ID,
          secretAccessKey: import.meta.env.VITE_AWS_SECRET_ACCESS_KEY,
        },
      });

      const docClient = DynamoDBDocumentClient.from(client);

      const command = new ScanCommand({
        TableName: 'jobs',
      });

      try {
        const result = await docClient.send(command);
        if (result.Items) {
          const sortedJobs = (result.Items as Job[]).sort(
            (a, b) =>
              new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          );
          setJobListings(sortedJobs);
        }
      } catch (error) {
        console.error('Error fetching jobs from DynamoDB:', error);
      }
    };

    fetchJobs();
  }, []);

  const handleJobSelect = (id: string) => {
    setSelectedJobId(id);
    navigate(`/jobs/${id}`);
  };

  const getRelativeTime = (timestamp: string) => {
    const now = new Date();
    const jobDate = new Date(timestamp);
    const diffInSeconds = Math.floor(
      (now.getTime() - jobDate.getTime()) / 1000
    );

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600)
      return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400)
      return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    return `${Math.floor(diffInSeconds / 86400)} days ago`;
  };

  return (
    <div className='flex h-screen'>
      {/* Sidebar */}
      <div className='w-1/3 border-r'>
        <Card className='h-full rounded-none'>
          <CardHeader className='pb-2'>
            <CardTitle className='text-2xl font-bold'>Recent Jobs</CardTitle>
          </CardHeader>
          <CardContent className='p-0'>
            <ScrollArea className='h-[calc(100vh-100px)]'>
              {jobListings.map((job) => (
                <div
                  key={job.website_jobid}
                  className='px-4 py-3 hover:bg-gray-50 transition-colors'
                >
                  <Button
                    variant={
                      job.website_jobid === selectedJobId
                        ? 'secondary'
                        : 'ghost'
                    }
                    className='w-full justify-start text-left p-0 h-auto'
                    onClick={() => handleJobSelect(job.website_jobid)}
                  >
                    <div className='flex flex-col items-start space-y-1'>
                      <div className='font-semibold text-lg'>{job.title}</div>
                      <div className='text-sm text-gray-600 flex items-center'>
                        <Briefcase className='h-4 w-4 mr-2' />
                        {job.company}
                      </div>
                      <div className='text-sm text-gray-600 flex items-center'>
                        <Clock className='h-4 w-4 mr-2' />
                        {getRelativeTime(job.timestamp)}
                      </div>
                      <div className='flex items-center space-x-2 mt-1'>
                        <Badge
                          variant='secondary'
                          className='px-2 py-1 text-xs'
                        >
                          {job.location}
                        </Badge>
                        <Badge variant='outline' className='px-2 py-1 text-xs'>
                          {job.website_jobid.startsWith('dice_')
                            ? 'Dice'
                            : 'Indeed'}
                        </Badge>
                      </div>
                    </div>
                  </Button>
                </div>
              ))}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Job Details */}
      <div className='w-2/3 p-4'>
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

export default JobListingPage;
