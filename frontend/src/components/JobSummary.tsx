import { Job } from '@/types/job';
import {
  Users,
  Package,
  Code,
  CheckSquare,
  FileText,
  Star,
} from 'lucide-react';
import { SummarySection } from '@/helpers/SummarySection';
import CompanyDetails from './CompanyDetails';
import { Separator } from '@radix-ui/react-separator';

const JobSummary = ({ job }: { job: Job }) => {
  return (
    <div className='bg-white rounded-lg p-6'>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
        <div className='space-y-6'>
          <SummarySection
            title='Technology Stack'
            items={job.technology_stack}
            icon={<Code className='h-5 w-5' />}
            columns={2}
          />
          <SummarySection
            title='Requirements'
            items={job.requirements}
            icon={<FileText className='h-5 w-5' />}
          />
        </div>
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
            title='Key Responsibilities'
            items={job.key_responsibilities}
            icon={<CheckSquare className='h-5 w-5' />}
          />
          <SummarySection
            title='Exceptional Perks'
            items={job.exceptional_perks}
            icon={<Star className='h-5 w-5' />}
          />
        </div>
      </div>
      {job.company_info && (
        <>
          <Separator className='my-6' />
          <CompanyDetails job={job} />
        </>
      )}
    </div>
  );
};

export default JobSummary;
