import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate,
} from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import JobDetails from './components/JobDetails';
import JobListingShell from './components/JobListingShell';

const NotFound: React.FC = () => {
  return (
    <div className='flex flex-col items-center justify-center h-full'>
      <h1 className='text-4xl font-bold mb-4'>404 - Page Not Found</h1>
      <p className='text-xl mb-8'>The page you're looking for doesn't exist.</p>
      <Link to='/jobs'>
        <Button variant='default'>Go to Jobs</Button>
      </Link>
    </div>
  );
};

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className='min-h-screen flex flex-col'>
          <main className='flex-grow'>
            <Routes>
              <Route path='/' element={<Navigate to='/jobs' replace />} />
              <Route path='/jobs' element={<JobListingShell />}>
                <Route path=':jobId' element={<JobDetails />} />
              </Route>
              <Route path='*' element={<NotFound />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
