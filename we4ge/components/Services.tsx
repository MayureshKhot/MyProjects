import React from 'react';
import { Database, Bot, CircuitBoard, LucideIcon } from 'lucide-react';
import { Service } from '../types';

const services: Service[] = [
  {
    id: 'mern',
    title: 'MERN Stack Architecture',
    description: 'Scalable, lightning-fast web applications built on MongoDB, Express, React, and Node.js. The backbone of your digital operation.',
    icon: Database,
    gradient: 'from-blue-500 to-cyan-400'
  },
  {
    id: 'ai',
    title: 'Autonomous AI Agents',
    description: 'We build intelligent agents that handle support, sales, and analysis 24/7. Not just chatbots, but active workers in your business.',
    icon: Bot,
    gradient: 'from-purple-500 to-pink-500'
  },
  {
    id: 'automation',
    title: 'n8n Automations',
    description: 'Connect your disparate tools into a unified war machine. We remove manual grunt work so you can focus on strategy.',
    icon: CircuitBoard,
    gradient: 'from-emerald-500 to-green-400'
  }
];

export const Services: React.FC = () => {
  return (
    <section id="capabilities" className="py-24 bg-[#050505] relative">
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-gray-800 to-transparent" />
      
      <div className="container mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-forge-500 font-bold tracking-[0.2em] uppercase mb-4 text-sm">Capabilities</h2>
          <h3 className="text-4xl md:text-5xl font-display font-bold text-white">
            We Forge <span className="text-gray-500">Three Pillars</span>
          </h3>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <div 
              key={service.id}
              className="group relative p-8 rounded-2xl bg-dark-800 border border-white/5 hover:border-forge-500/50 transition-all duration-500 hover:-translate-y-2 overflow-hidden"
            >
              {/* Background Glow on Hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-forge-900/0 to-forge-900/0 group-hover:from-forge-900/20 group-hover:to-transparent transition-all duration-500" />
              
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${service.gradient} p-0.5 mb-6 group-hover:shadow-[0_0_20px_rgba(255,255,255,0.2)] transition-shadow`}>
                <div className="w-full h-full bg-black rounded-[10px] flex items-center justify-center">
                  <service.icon className="w-7 h-7 text-white" />
                </div>
              </div>

              <h4 className="text-2xl font-bold text-white mb-4 group-hover:text-forge-400 transition-colors">
                {service.title}
              </h4>
              <p className="text-gray-400 leading-relaxed relative z-10">
                {service.description}
              </p>
              
              {/* Decorative line */}
              <div className="absolute bottom-0 left-0 h-1 w-0 bg-forge-500 group-hover:w-full transition-all duration-700 ease-out" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};