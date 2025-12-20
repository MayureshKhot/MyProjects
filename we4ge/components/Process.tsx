import React from 'react';

const steps = [
  {
    num: '01',
    name: 'Raw Ore',
    desc: 'Discovery & Strategy. We identify the raw problem and the purest solution.',
  },
  {
    num: '02',
    name: 'The Heat',
    desc: 'Rapid Prototyping & Design. We melt down complexity into intuitive UX.',
  },
  {
    num: '03',
    name: 'Hammering',
    desc: 'Development. Heavy hitting coding cycles. MERN stack implementation.',
  },
  {
    num: '04',
    name: 'Sharpening',
    desc: 'Refinement & Testing. Honing performance, security, and AI accuracy.',
  },
  {
    num: '05',
    name: 'Deploy',
    desc: 'Launch. Your weapon is shipped to the battlefield, ready for war.',
  },
];

export const Process: React.FC = () => {
  return (
    <section id="process" className="py-24 bg-dark-900 relative overflow-hidden">
        {/* Subtle background texture */}
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-forge-900 via-black to-black"></div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="mb-20">
            <h2 className="text-forge-500 font-bold tracking-[0.2em] uppercase mb-4 text-sm">The Process</h2>
            <h3 className="text-4xl md:text-5xl font-display font-bold text-white max-w-2xl">
                From Raw Idea to <br />
                <span className="text-white">Cold Hard Steel</span>
            </h3>
        </div>

        <div className="relative">
          {/* Central Line */}
          <div className="absolute left-[15px] md:left-1/2 top-0 bottom-0 w-0.5 bg-gray-800 md:-translate-x-1/2">
            <div className="absolute top-0 w-full h-1/2 bg-gradient-to-b from-forge-500 to-transparent opacity-50"></div>
          </div>

          <div className="flex flex-col gap-12 md:gap-24">
            {steps.map((step, idx) => (
              <div 
                key={step.num} 
                className={`flex flex-col md:flex-row items-start ${idx % 2 === 0 ? 'md:flex-row-reverse' : ''} gap-8 md:gap-0`}
              >
                {/* Text Side */}
                <div className={`w-full md:w-1/2 ${idx % 2 === 0 ? 'md:pl-16' : 'md:pr-16 md:text-right'}`}>
                  <span className="text-6xl font-display font-bold text-gray-800 block mb-2">{step.num}</span>
                  <h4 className="text-2xl font-bold text-white mb-2">{step.name}</h4>
                  <p className="text-gray-400 leading-relaxed">{step.desc}</p>
                </div>

                {/* Center Node */}
                <div className="absolute left-[6px] md:left-1/2 md:-translate-x-1/2 w-5 h-5 rounded-full border-4 border-dark-900 bg-forge-600 shadow-[0_0_15px_rgba(234,88,12,0.8)] z-10 mt-16 md:mt-2"></div>

                {/* Empty Side for layout balance */}
                <div className="hidden md:block w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};