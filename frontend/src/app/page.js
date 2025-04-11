"use client";

import Image from 'next/image';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import Header from '@/components/Header';

const images = [
  '/heroImage/image1.jpg', // Replace with the actual image paths in the public folder
  '/heroImage/image2.jpg',
  '/heroImage/image3.avif'
];

export default function ExamGuardPage() {
  const [currentSlide, setCurrentSlide] = useState(0);

  // Automatically switch slides every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % images.length);
    }, 5000); // 5000 ms (5 seconds)
    return () => clearInterval(interval); // Clear interval on unmount
  }, []);

  return (
    <div className="bg-black min-h-screen text-white gap-4 mb-4">
      {/* Header */}
      <Header navItems={[{ name: 'Pricing', url: '/Pricing' }]}
              buttons={[{ name: 'Login', url: '/login' }]}/>

      {/* Hero Section with Sliding Images */}
      <section className="flex flex-col items-center text-center py-16 px-16 relative">
        <div className="relative w-full max-w-8xl h-[600px] bg-gray-800 rounded-lg overflow-hidden">
          {/* Loop over images */}
          {images.map((src, index) => (
            <div
              key={index}
              className={`absolute inset-0 transition-opacity duration-1000 ${
                index === currentSlide ? 'opacity-100' : 'opacity-0'
              }`}
            >
              {/* <Image
                src={src}
                alt={`Slide ${index + 1}`}
                layout="fill"
                objectFit="cover"
                className="rounded-lg"
              /> */}
              <img
                src={src}
                alt={`Slide ${index + 1}`}
                className="rounded-lg w-full h-full object-cover"
              />

            </div>
          ))}

          {/* Overlay Text and Button */}
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 bg-black bg-opacity-50">
            <h2 className="text-3xl md:text-5xl font-inter">User our AI models to detect cheating on exams and store videos on the cloud for analysis</h2>
            <p className="mt-4 text-lg">Try our basic model for free by just uploading a video to get the classified activity</p>
            <Link href="/login" className="mt-6 bg-blue-600 text-white py-2 px-6 rounded-xl 
        hover:bg-blue-700 transition">Try it</Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="text-center px-6 py-12 max-w-5xl mx-auto">
        <h3 className="text-2xl font-inter mb-6">Why choose ExamGuard?</h3>
        <p className="text-gray-400 max-w-3xl mx-auto mb-12">ExamGuard is the most advanced solution for proctoring exams. Our AI technology can classify cheating behaviors ,allowing instructors to protect exams at scale without compromising exam integrity.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center">
            <img src="/heroimage2/image2.jpg" alt="Proctor exams at scale" className="w-50 h-50 mb-4" /> {/* Replace with actual icons */}
            <h4 className="text-xl font-semibold">Proctor exams at scale</h4>
            <p className="text-gray-400 mt-2">Monitor multiple exam videos, ensuring a fair testing environment.</p>
          </div>
          <div className="flex flex-col items-center">
            <img src="/heroimage2/image3.jpg" alt="Detect cheating behavior" className="w-50 h-50 mb-4" /> {/* Replace with actual icons */}
            <h4 className="text-xl font-semibold">Detect cheating behavior</h4>
            <p className="text-gray-400 mt-2">Use our advanced machine learning and deep learning algorithms to detect suspicious actions during exams.</p>
          </div>
          <div className="flex flex-col items-center">
            <img src="/heroimage2/image1.jpg" alt="Get video analysis" className="w-50 h-50 mb-4" /> {/* Replace with actual icons */}
            <h4 className="text-xl font-semibold ">Get video analysis</h4>
            <p className="text-gray-400 mt-2">Upload your own videos and get analysis of cheating behavior</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-6 text-gray-400">
        <p>&copy; 2025 ExamGuard. All rights reserved.</p>
      </footer>
    </div>
  );
}
