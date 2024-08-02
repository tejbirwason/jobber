import { Job } from '@/types/job';
import React from 'react';
import {
  Users,
  Package,
  Code,
  CheckSquare,
  FileText,
  Star,
} from 'lucide-react';

const SummarySection: React.FC<{
  title: string;
  items?: string[];
  icon: React.ReactNode;
  columns?: number;
}> = ({ title, items, icon, columns = 1 }) => {
  if (!items || items.length === 0) return null;
  return (
    <div className='mb-4'>
      <h4 className='font-semibold text-gray-700 mb-2 flex items-center'>
        {icon}
        <span className='ml-2'>{title}</span>
      </h4>
      <ul
        className={`list-disc pl-5 space-y-1 ${
          columns === 2 ? 'columns-2' : ''
        }`}
      >
        {items.map((item, index) => (
          <li key={index} className='text-gray-600'>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
};

const JobSummary = ({ job }: { job: Job }) => {
  return (
    <div className='bg-white rounded-lg p-6'>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
        <div className='space-y-6'>
          <SummarySection
            title='Team Information'
            items={job.team_information}
            icon={<Users className='h-5 w-5' />}
          />
          <SummarySection
            title='Product Information'
            items={job.product_information}
            icon={<Package className='h-5 w-5' />}
          />
        </div>
        <div className='space-y-6'>
          <SummarySection
            title='Technology Stack'
            items={job.technology_stack}
            icon={<Code className='h-5 w-5' />}
            columns={2}
          />
          <SummarySection
            title='Key Responsibilities'
            items={job.key_responsibilities}
            icon={<CheckSquare className='h-5 w-5' />}
          />
        </div>
        <div className='space-y-6'>
          <SummarySection
            title='Requirements'
            items={job.requirements}
            icon={<FileText className='h-5 w-5' />}
          />
          <SummarySection
            title='Exceptional Perks'
            items={job.exceptional_perks}
            icon={<Star className='h-5 w-5' />}
          />
        </div>
      </div>
    </div>
  );
};

export default JobSummary;
