import { LucideIcon } from 'lucide-react';

export interface Service {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
  gradient: string;
}

export interface ProcessStep {
  number: string;
  title: string;
  description: string;
}

export interface Project {
  id: string;
  title: string;
  category: string;
  outcome: string;
  image: string;
}