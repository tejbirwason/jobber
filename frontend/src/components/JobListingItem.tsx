import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Briefcase, Clock, MapPin, Circle } from 'lucide-react';
import { Job } from '@/types/job';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, UpdateCommand } from '@aws-sdk/lib-dynamodb';
import { useJobs } from '@/hooks/useJobs';

interface JobListingItemProps {
  job: Job;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

const JobListingItem: React.FC<JobListingItemProps> = ({
  job,
  isSelected,
  onSelect,
}) => {
  const { markJobAsSeen } = useJobs();

  const getRelativeTime = (timestamp: string) => {
    const now = new Date();
    const jobDate = new Date(timestamp + 'Z'); // Append 'Z' to treat as UTC
    const localJobDate = new Date(jobDate.toLocaleString()); // Convert to local time
    const diffInSeconds = Math.floor(
      (now.getTime() - localJobDate.getTime()) / 1000
    );

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600)
      return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400)
      return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    return `${Math.floor(diffInSeconds / 86400)} days ago`;
  };

  const handleClick = async () => {
    onSelect(job.id);
    markJobAsSeen(job.id);

    // Update DynamoDB record
    const client = new DynamoDBClient({
      region: 'us-east-1',
      credentials: {
        accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY_ID,
        secretAccessKey: import.meta.env.VITE_AWS_SECRET_ACCESS_KEY,
      },
    });

    const docClient = DynamoDBDocumentClient.from(client);

    const command = new UpdateCommand({
      TableName: 'jobs',
      Key: {
        id: job.id,
      },
      UpdateExpression: 'SET seen = :seen',
      ExpressionAttributeValues: {
        ':seen': true,
      },
    });

    try {
      await docClient.send(command);
      console.log(`Job ${job.id} marked as seen in DynamoDB`);
    } catch (error) {
      console.error('Error updating DynamoDB:', error);
    }
  };

  return (
    <div className='px-6 py-4 hover:bg-gray-50 transition-colors rounded-lg shadow-sm'>
      <Button
        variant={isSelected ? 'secondary' : 'ghost'}
        className='w-full justify-start text-left p-0 h-auto'
        onClick={handleClick}
      >
        <div className='flex flex-col items-start space-y-2 w-full'>
          <div className='font-bold text-xl text-primary break-words w-full flex items-center'>
            {!job.seen && (
              <Circle className='h-3 w-3 mr-2 text-blue-500 fill-current' />
            )}
            {job.title}
          </div>
          <div className='text-sm text-gray-600 flex items-center'>
            <Briefcase className='h-4 w-4 mr-2 text-primary flex-shrink-0' />
            <span className='font-medium break-words'>{job.company}</span>
          </div>
          <div className='text-sm text-gray-500 flex items-center'>
            <Clock className='h-4 w-4 mr-2 text-primary' />
            {getRelativeTime(job.timestamp)}
          </div>
          <div className='text-sm text-gray-500 flex items-center'>
            <MapPin className='h-4 w-4 mr-2 text-primary' />
            {job.location}
          </div>
          <div className='flex items-center space-x-2 mt-2'>
            <Badge
              variant={job.id.startsWith('dice_') ? 'secondary' : 'default'}
              className='px-3 py-1 text-xs font-semibold rounded-full'
              style={{
                backgroundColor: job.id?.startsWith('dice_')
                  ? '#8B5CF6' // A pleasant purple for Dice
                  : '#3B82F6', // A pleasant blue for Indeed
                color: 'white',
              }}
            >
              {job.id.startsWith('dice_') ? 'Dice' : 'Indeed'}
            </Badge>
          </div>
        </div>
      </Button>
    </div>
  );
};

export default JobListingItem;
