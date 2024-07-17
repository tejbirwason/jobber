import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useParams,
} from 'react-router-dom';
import { Button } from '@/components/ui/button';

// Import your components
import JobListingPage from './components/JobListingPage';

// Placeholder for individual job component
const JobDetails: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  return <div>Job Details for Job ID: {jobId}</div>;
};

const App: React.FC = () => {
  return (
    <Router>
      <div className='min-h-screen flex flex-col'>
        <header className='bg-gray-800 text-white p-4'>
          <nav>
            <Link to='/jobs'>
              <Button variant='ghost'>Jobs</Button>
            </Link>
          </nav>
        </header>

        <main className='flex-grow'>
          <Routes>
            <Route path='/jobs' element={<JobListingPage />}>
              <Route path=':jobId' element={<JobDetails />} />
            </Route>
            <Route path='*' element={<JobListingPage />} />
          </Routes>
        </main>

        <footer className='bg-gray-800 text-white p-4 text-center'>
          © 2024 Job Tracking App
        </footer>
      </div>
    </Router>
  );
};

export default App;
