import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { MeshDistortMaterial, Float, Stars, Sparkles } from '@react-three/drei';
import * as THREE from 'three';

const MoltenCore = () => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      // Rotate the core
      meshRef.current.rotation.x = state.clock.getElapsedTime() * 0.2;
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.3;
      
      // Pulse scale slightly
      const scale = 1 + Math.sin(state.clock.getElapsedTime()) * 0.05;
      meshRef.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <Float speed={1.5} rotationIntensity={0.5} floatIntensity={1}>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[2.8, 4]} />
        <MeshDistortMaterial
          color="#ea580c"
          emissive="#7c2d12"
          emissiveIntensity={0.8}
          roughness={0.2}
          metalness={1}
          distort={0.6}
          speed={2}
        />
      </mesh>
    </Float>
  );
};

const EmberParticles = () => {
  return (
    <Sparkles 
      count={150} 
      scale={12} 
      size={6} 
      speed={0.4} 
      opacity={0.7} 
      color="#fdba74"
    />
  );
};

export const Scene: React.FC = () => {
  return (
    <div className="absolute inset-0 z-0 h-screen w-full pointer-events-none">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <color attach="background" args={['#050505']} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#fb923c" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#38bdf8" />
        
        <MoltenCore />
        <EmberParticles />
      </Canvas>
      {/* Gradient Overlay to blend 3D into DOM content */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#050505] z-10" />
      <div className="absolute inset-0 bg-gradient-to-r from-[#050505]/80 via-transparent to-[#050505]/80 z-10" />
    </div>
  );
};