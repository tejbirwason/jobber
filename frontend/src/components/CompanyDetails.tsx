import React from 'react';
import {
  Building,
  Package,
  DollarSign,
  User,
  FileText,
  MapPin,
  Link,
  Clock,
  Cpu,
  Coffee,
  Globe,
  Linkedin,
} from 'lucide-react';
import { SummarySection } from '@/helpers/SummarySection';
import { Job } from '@/types/job';

interface CompanyDetailsProps {
  job?: Job;
}

const CompanyDetails: React.FC<CompanyDetailsProps> = ({ job }) => {
  if (!job || !job.company_info) return null;

  const companyInfo = job.company_info;

  return (
    <div className='col-span-full mt-8'>
      <div className='flex items-center justify-between mb-4'>
        <h2 className='text-2xl font-semibold'>{job.company}</h2>
        <div className='space-x-2'>
          {companyInfo.key_links?.official && (
            <a
              href={companyInfo.key_links.official}
              target='_blank'
              rel='noopener noreferrer'
              className='inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gray-600 hover:bg-gray-700 transition duration-150 ease-in-out shadow-sm'
            >
              <Globe className='h-4 w-4 mr-2' />
              Website
            </a>
          )}
          {companyInfo.key_links?.linkedin && (
            <a
              href={companyInfo.key_links.linkedin}
              target='_blank'
              rel='noopener noreferrer'
              className='inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gray-600 hover:bg-gray-700 transition duration-150 ease-in-out shadow-sm'
            >
              <Linkedin className='h-4 w-4 mr-2' />
              LinkedIn
            </a>
          )}
        </div>
      </div>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
        <div className='space-y-6 bg-gray-50 p-4 rounded-md'>
          <SummarySection
            title='Products & Services'
            items={companyInfo.products_services}
            icon={<Package className='h-5 w-5' />}
          />
          <SummarySection
            title='Financials'
            items={companyInfo.financials}
            icon={<DollarSign className='h-5 w-5' />}
          />
          <SummarySection
            title='Leadership'
            items={companyInfo.leadership}
            icon={<User className='h-5 w-5' />}
          />
        </div>
        <div className='space-y-6'>
          <SummarySection
            title='Business Description'
            items={companyInfo.business_description}
            icon={<FileText className='h-5 w-5' />}
          />
          <SummarySection
            title='Key Locations'
            items={companyInfo.key_locations}
            icon={<MapPin className='h-5 w-5' />}
          />
          <SummarySection
            title='Key Links'
            items={[
              ...(companyInfo.key_links?.official
                ? [
                    `<a href="${companyInfo.key_links.official}" target="_blank" rel="noopener noreferrer" class="text-gray-600 hover:underline">Official Website</a>`,
                  ]
                : []),
              ...(companyInfo.key_links?.other || []).map(
                (link, index) =>
                  `<a href="${link}" target="_blank" rel="noopener noreferrer" class="text-gray-600 hover:underline">Other Link ${
                    index + 1
                  }</a>`
              ),
              ...(companyInfo.key_links?.linkedin
                ? [
                    `<a href="${companyInfo.key_links.linkedin}" target="_blank" rel="noopener noreferrer" class="text-gray-600 hover:underline">LinkedIn</a>`,
                  ]
                : []),
            ]}
            icon={<Link className='h-5 w-5' />}
          />
        </div>
        <div className='space-y-6 bg-gray-50 p-4 rounded-md'>
          <SummarySection
            title='History'
            items={companyInfo.history}
            icon={<Clock className='h-5 w-5' />}
          />
          <SummarySection
            title='Technology'
            items={companyInfo.technology}
            icon={<Cpu className='h-5 w-5' />}
          />
          <SummarySection
            title='Corporate Culture'
            items={companyInfo.corporate_culture}
            icon={<Coffee className='h-5 w-5' />}
          />
          <SummarySection
            title='Company Overview'
            items={companyInfo.company_overview}
            icon={<Building className='h-5 w-5' />}
          />
        </div>
      </div>
    </div>
  );
};

export default CompanyDetails;
