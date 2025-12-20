import React from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { Services } from './components/Services';
import { Process } from './components/Process';
import { Work } from './components/Work';
import { Contact } from './components/Contact';

function App() {
  return (
    <div className="bg-black min-h-screen text-white selection:bg-forge-500 selection:text-white">
      <Navbar />
      <main>
        <Hero />
        <Services />
        <Process />
        <Work />
        <Contact />
      </main>
    </div>
  );
}

export default App;