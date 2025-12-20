import React from 'react';
import { ExternalLink, TrendingUp, Zap, Clock } from 'lucide-react';
import { Project } from '../types';

const projects: Project[] = [
  {
    id: '1',
    title: 'FinTech Core Migration',
    category: 'MERN Architecture',
    outcome: 'Processed $2M+ in transactions within first month. 40% reduction in latency.',
    image: 'https://picsum.photos/800/600?random=1'
  },
  {
    id: '2',
    title: 'SupportGenie Agent',
    category: 'AI Agent Deployment',
    outcome: 'Reduced support ticket volume by 75% using autonomous RAG pipeline.',
    image: 'https://picsum.photos/800/600?random=2'
  },
  {
    id: '3',
    title: 'SaaS Onboarding Flow',
    category: 'n8n Automation',
    outcome: 'Automated 12 manual touchpoints, saving the sales team 20 hours/week.',
    image: 'https://picsum.photos/800/600?random=3'
  }
];

export const Work: React.FC = () => {
  return (
    <section id="work" className="py-24 bg-[#080808]">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
          <div>
            <h2 className="text-forge-500 font-bold tracking-[0.2em] uppercase mb-4 text-sm">The Armory</h2>
            <h3 className="text-4xl md:text-5xl font-display font-bold text-white">
              Recent <span className="text-gray-500">Battles Won</span>
            </h3>
          </div>
          <a href="#" className="flex items-center gap-2 text-white border-b border-forge-500 pb-1 hover:text-forge-400 transition-colors">
            View All Projects <ExternalLink className="w-4 h-4" />
          </a>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {projects.map((project, idx) => (
            <div key={project.id} className="group cursor-pointer">
              <div className="relative overflow-hidden rounded-lg mb-6 aspect-[4/3]">
                <div className="absolute inset-0 bg-forge-900/20 group-hover:bg-transparent transition-colors z-10" />
                <img 
                  src={project.image} 
                  alt={project.title} 
                  className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-700 filter grayscale group-hover:grayscale-0"
                />
                
                {/* Floating metric badge */}
                <div className="absolute bottom-4 left-4 z-20 bg-black/80 backdrop-blur border border-white/10 px-4 py-2 rounded flex items-center gap-2 text-xs font-bold text-forge-400">
                    {idx === 0 ? <TrendingUp className="w-3 h-3" /> : idx === 1 ? <Zap className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                    RESULT
                </div>
              </div>
              
              <div className="space-y-2">
                <span className="text-forge-500 text-xs font-bold uppercase tracking-wider">{project.category}</span>
                <h4 className="text-xl font-bold text-white group-hover:text-forge-400 transition-colors">{project.title}</h4>
                <p className="text-gray-400 text-sm leading-relaxed border-l-2 border-gray-800 pl-4 py-1">
                  {project.outcome}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};