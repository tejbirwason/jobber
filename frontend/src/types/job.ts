export interface Job {
  id: string;
  timestamp: string;
  company: string;
  description?: string;
  description_html?: string;
  company_link?: string;
  company_image?: string;
  employment_type?: string;
  date_posted: string;
  link: string;
  location: string;
  title: string;
  posted_date?: string;
  category?: string;
  category_explanation?: string;
  seen?: boolean;
}