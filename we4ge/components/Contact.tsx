import React, { useState } from 'react';
import { Mail, CheckCircle } from 'lucide-react';

export const Contact: React.FC = () => {
  const [formState, setFormState] = useState<'idle' | 'submitting' | 'success'>('idle');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormState('submitting');
    // Simulate API call
    setTimeout(() => {
      setFormState('success');
    }, 1500);
  };

  return (
    <footer id="contact" className="bg-black relative pt-32 pb-12 overflow-hidden">
      {/* Background glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-forge-600/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="container mx-auto px-6 relative z-10">
        <div className="max-w-4xl mx-auto text-center mb-16">
          <h2 className="text-5xl md:text-7xl font-display font-black text-white mb-8">
            READY TO <span className="text-forge-500">FORGE</span>?
          </h2>
          <p className="text-xl text-gray-400 mb-12">
            Your competition isn't waiting. Neither should you. <br/>
            Let's build the weapon that wins your market.
          </p>

          {formState === 'success' ? (
            <div className="bg-forge-900/20 border border-forge-500/50 rounded-xl p-8 flex flex-col items-center justify-center animate-fade-in">
              <CheckCircle className="w-16 h-16 text-forge-500 mb-4" />
              <h3 className="text-2xl font-bold text-white mb-2">Message Received</h3>
              <p className="text-gray-400">The blacksmiths are reviewing your request. Expect a signal within 24 hours.</p>
              <button 
                onClick={() => setFormState('idle')}
                className="mt-6 text-sm text-forge-400 hover:text-forge-300 underline"
              >
                Send another message
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="bg-dark-800 border border-white/10 p-8 rounded-2xl max-w-lg mx-auto shadow-2xl">
              <div className="space-y-4 text-left">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Your Name</label>
                  <input 
                    required 
                    type="text" 
                    placeholder="John Doe" 
                    className="w-full bg-black border border-gray-800 rounded p-4 text-white focus:border-forge-500 focus:outline-none focus:ring-1 focus:ring-forge-500 transition-all" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Email Address</label>
                  <input 
                    required 
                    type="email" 
                    placeholder="john@company.com" 
                    className="w-full bg-black border border-gray-800 rounded p-4 text-white focus:border-forge-500 focus:outline-none focus:ring-1 focus:ring-forge-500 transition-all" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Challenge</label>
                  <textarea 
                    rows={3} 
                    placeholder="What do you need built?" 
                    className="w-full bg-black border border-gray-800 rounded p-4 text-white focus:border-forge-500 focus:outline-none focus:ring-1 focus:ring-forge-500 transition-all" 
                  />
                </div>
                <button 
                  disabled={formState === 'submitting'}
                  type="submit" 
                  className="w-full bg-forge-600 hover:bg-forge-500 text-white font-bold uppercase tracking-wider py-4 rounded transition-all flex items-center justify-center gap-2"
                >
                  {formState === 'submitting' ? 'Forging...' : 'Initiate Protocol'} 
                  {!formState && <Mail className="w-4 h-4" />}
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between text-gray-600 text-sm">
          <p>&copy; {new Date().getFullYear()} we4ge. All rights reserved.</p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-forge-500 transition-colors">Twitter</a>
            <a href="#" className="hover:text-forge-500 transition-colors">LinkedIn</a>
            <a href="#" className="hover:text-forge-500 transition-colors">GitHub</a>
          </div>
        </div>
      </div>
    </footer>
  );
};