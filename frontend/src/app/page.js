"use client";

import Link from 'next/link';
import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import { motion } from "framer-motion";

const images = [
  '/heroImage/image1.jpeg',
  '/heroImage/image2.jpeg',
  '/heroImage/image3.jpeg'
];

const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const stagger = {
  visible: {
    transition: {
      staggerChildren: 0.2
    }
  }
};

export default function ExamGuardPage() {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % images.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white min-h-screen text-gray-900 gap-4 mb-4">
      <Header navItems={[{ name: 'Pricing', url: '/Pricing' }]} buttons={[{ name: 'Login', url: '/login' }]} />

      {/* Hero Section */}
      <motion.section
        className="flex flex-col md:flex-row items-center justify-between py-16 px-6 md:px-16 bg-white"
        initial="hidden"
        animate="visible"
        variants={stagger}
      >
        <motion.div className="md:w-1/2 mb-10 md:mb-0" variants={fadeInUp}>
          <h2 className="text-3xl md:text-5xl font-bold text-gray-900 leading-tight">
            Use our AI models to detect cheating on exams and store videos on the cloud for analysis
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Try our basic model for free by just uploading a video to get the classified activity.
          </p>
          <Link
            href="/login"
            className="mt-6 inline-block bg-purple-600 text-white font-medium py-2 px-6 rounded-lg hover:bg-purple-700 transition"
          >
            Try it
          </Link>
        </motion.div>

        <motion.div className="md:w-1/2 w-full h-[350px] md:h-[500px] rounded-lg overflow-hidden relative" variants={fadeInUp}>
          {images.map((src, index) => (
            <div
              key={index}
              className={`absolute inset-0 transition-opacity duration-1000 ${index === currentSlide ? 'opacity-100' : 'opacity-0'}`}
            >
              <img
                src={src}
                alt={`Slide ${index + 1}`}
                className="w-full h-full object-cover rounded-lg"
              />
            </div>
          ))}
        </motion.div>
      </motion.section>

      {/* Features Section */}
      <section className="bg-white py-14 px-6 md:px-12 max-w-7xl mx-auto text-center">
        <motion.h3
          className="text-3xl md:text-4xl font-bold text-gray-900 mb-6"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          Why choose ExamGuard?
        </motion.h3>

        <motion.p
          className="text-gray-600 text-lg max-w-3xl mx-auto mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          ExamGuard is the most advanced solution for proctoring exams. Our AI technology classifies cheating behaviors, allowing instructors to protect exams at scale without compromising integrity.
        </motion.p>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={stagger}
        >
          {[{
            title: "Proctor exams at scale",
            text: "Monitor multiple exam videos by storing them in the cloud, ensuring a fair testing environment.",
            img: "/heroimage2/image2.jpg"
          }, {
            title: "Detect cheating behavior",
            text: "Use our advanced machine learning pipelines to detect suspicious actions during exams.",
            img: "/heroimage2/image3.jpg"
          }, {
            title: "Get video analysis",
            text: "Upload your own videos and get detailed analysis of cheating behavior.",
            img: "/heroimage2/image1.jpg"
          }].map((feature, i) => (
            <motion.div key={i} className="flex flex-col items-center text-center px-4" variants={fadeInUp}>
              <img src={feature.img} alt={feature.title} className="w-full h-52 object-cover rounded-xl shadow-md mb-6" />
              <h4 className="text-xl font-semibold text-gray-900">{feature.title}</h4>
              <p className="text-gray-600 mt-2">{feature.text}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="text-center py-6 text-gray-900">
        <p>&copy; 2025 ExamGuard. All rights reserved.</p>
      </footer>
    </div>
  );
}
