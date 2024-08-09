import React from 'react';

const SummarySection: React.FC<{
  title: string;
  items?: string[];
  icon: React.ReactNode;
}> = ({ title, items, icon }) => {
  if (!items || items.length === 0) return null;
  return (
    <div className='mb-4'>
      <h3 className='font-semibold text-gray-700 mb-2 flex items-center text-lg'>
        {icon}
        <span className='ml-2'>{title}</span>
      </h3>
      <ul className='list-disc pl-5 space-y-1'>
        {items.map((item, index) => (
          <li key={index} className='text-gray-600'>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
};

export { SummarySection };
