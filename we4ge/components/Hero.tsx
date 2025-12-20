import React from 'react';
import { ArrowRight, ChevronDown } from 'lucide-react';
import { Scene } from './Scene';
import { motion } from 'framer-motion';

// Workaround for framer-motion type issues in current environment
const MotionDiv = motion.div as any;
const MotionH1 = motion.h1 as any;
const MotionP = motion.p as any;

export const Hero: React.FC = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <Scene />
      
      <div className="relative z-20 container mx-auto px-6 text-center">
        <MotionDiv
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="inline-block mb-4 px-4 py-1.5 rounded-full border border-forge-500/30 bg-forge-500/10 backdrop-blur-sm"
        >
          <span className="text-forge-400 text-xs md:text-sm font-bold tracking-[0.2em] uppercase">
            Startups • Enterprise • Scale-ups
          </span>
        </MotionDiv>

        <MotionH1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="text-5xl md:text-7xl lg:text-9xl font-display font-black text-white mb-6 leading-tight tracking-tight"
        >
          WE FORGE <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-forge-400 via-forge-500 to-yellow-500 drop-shadow-[0_0_30px_rgba(234,88,12,0.3)]">
            YOUR WEAPON
          </span>
        </MotionH1>

        <MotionP
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.6 }}
          className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed font-light"
        >
          In a market of generic tools, we build Excaliburs. 
          Custom MERN stack applications, autonomous AI agents, and 
          unbreakable automations designed for one purpose: <strong className="text-gray-200">Dominance.</strong>
        </MotionP>

        <MotionDiv
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <a
            href="#contact"
            className="group relative px-8 py-4 bg-white text-black font-bold text-lg uppercase tracking-wide overflow-hidden rounded hover:bg-gray-200 transition-all duration-300"
          >
            <span className="relative z-10 flex items-center gap-2">
              Start The Fire <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </span>
          </a>
          
          <a
            href="#work"
            className="px-8 py-4 bg-transparent border border-gray-700 text-white font-medium text-lg uppercase tracking-wide rounded hover:border-forge-500 hover:text-forge-400 transition-colors duration-300"
          >
            View The Armory
          </a>
        </MotionDiv>
      </div>

      <MotionDiv
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 1 }}
        className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20 animate-bounce"
      >
        <ChevronDown className="w-8 h-8 text-gray-600" />
      </MotionDiv>
    </section>
  );
};