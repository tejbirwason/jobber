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
