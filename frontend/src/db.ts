import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  ScanCommand,
  UpdateCommand,
} from '@aws-sdk/lib-dynamodb';
import { Job } from './types/job';

const client = new DynamoDBClient({
  region: 'us-east-1',
  credentials: {
    accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY_ID,
    secretAccessKey: import.meta.env.VITE_AWS_SECRET_ACCESS_KEY,
  },
});

const docClient = DynamoDBDocumentClient.from(client);

export const fetchJobs = async (): Promise<Job[]> => {
  let allItems: Job[] = [];
  let lastEvaluatedKey: Record<string, any> | undefined;

  do {
    const command = new ScanCommand({
      TableName: 'jobs',
      ExclusiveStartKey: lastEvaluatedKey,
    });

    const result = await docClient.send(command);
    allItems = allItems.concat(result.Items as Job[]);
    lastEvaluatedKey = result.LastEvaluatedKey;
  } while (lastEvaluatedKey);

  // Filter jobs to only include those with specific IDs
  const targetJobIds = [
    'dice_85a43fea-df01-42e6-9449-f7c82ff3d9d2',
    'dice_a9dfb117-f96e-4b16-9166-fcfae0661747',
    'dice_ad552d63-65ee-4b81-a001-205d25dbe08b',
    'dice_0a16cf4c-8aca-4c78-b181-8a777b352e2e',
    'indeed_c69bd4df7e1d259d',
  ];
  allItems = allItems.filter((job) => targetJobIds.includes(job.id));

  return allItems;
};

export const updateJobCategory = async (
  jobId: string,
  newCategory: string
): Promise<void> => {
  const command = new UpdateCommand({
    TableName: 'jobs',
    Key: {
      id: jobId,
    },
    UpdateExpression: 'SET category = :category',
    ExpressionAttributeValues: {
      ':category': newCategory,
    },
  });

  try {
    await docClient.send(command);
  } catch (error) {
    console.error('Error updating job category:', error);
    throw error;
  }
};

export const updateJobSeen = async (jobId: string): Promise<void> => {
  const command = new UpdateCommand({
    TableName: 'jobs',
    Key: {
      id: jobId,
    },
    UpdateExpression: 'SET seen = :seen',
    ExpressionAttributeValues: {
      ':seen': true,
    },
  });

  try {
    await docClient.send(command);
  } catch (error) {
    console.error('Error updating job seen status:', error);
    throw error;
  }
};
