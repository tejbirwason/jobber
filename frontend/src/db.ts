import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, ScanCommand } from '@aws-sdk/lib-dynamodb';
import { Job } from './types/job';

export const fetchJobs = async (): Promise<Job[]> => {
  const client = new DynamoDBClient({
    region: 'us-east-1',
    credentials: {
      accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY_ID,
      secretAccessKey: import.meta.env.VITE_AWS_SECRET_ACCESS_KEY,
    },
  });

  const docClient = DynamoDBDocumentClient.from(client);
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
