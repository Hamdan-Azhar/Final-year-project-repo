"use client";

import { useState } from 'react';
import axios from 'axios';
import Image from 'next/image';
import Link from 'next/link';
import apiUrls from "../../backend_apis/apis";
import Header from '@/components/Header';
import Button from '@/components/Button';
import { useRouter } from "next/navigation";

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.post(apiUrls.resend_otp, { email });
      console.log(response.status, "----response.ok-------------", response.data);
      // Store email in localStorage before redirect
      localStorage.setItem('signup_email', email);
      
      // Store expiration time if available in response
      if (response.data.otp_expires_in) {
        const expiresAt = new Date();
        expiresAt.setSeconds(expiresAt.getSeconds() + response.data.otp_expires_in);
        localStorage.setItem('otp_expires_at', expiresAt.toISOString());
      }
      // Redirect to OTP page
      localStorage.setItem('otp_flow_type', 'password_reset'); 
      router.push('/otp');
    } catch (error) {
      if (error.response){
        setError(error.response.data.error);
      }
      // Clear any stored OTP data if signup fails
      localStorage.removeItem('signup_email');
      localStorage.removeItem('otp_expires_at');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-gray-300 flex flex-col items-center">
      {/* Navbar */}
      <Header/>
      {/* Card Wrapper for Main Content */}
      <div className="flex flex-col items-center justify-center flex-grow w-full px-4 mt-4">
        <div className="w-full max-w-sm bg-black p-6 rounded-lg shadow-lg">
          {/* Centered Title */}
          <h2 className="text-2xl font-semibold text-white text-center mb-6">
            Forgot your password?
          </h2>
          {/* Left-Aligned Description and Form */}
          <div className="w-full text-center space-y-4">
            {/* Error Message */}
            {error && (
              <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
            )}
            <p className="text-sm">
              Enter your email address and we&apos;ll send you otp to reset your password.
            </p>

            <form className="space-y-4" onSubmit={handleSubmit}>
              {/* Email Field */}
              <div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  // className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your email"
                />
              </div>

              {/* Send Reset Link Button */}
              <div className="flex justify-end">
              <Button
                type="submit"
                loading={isLoading}
                className="w-full"
                >
                  Send Reset link
              </Button>
              </div>
            </form>
            
            {/* Back to Sign In Link */}
            <div>
              <p className="text-sm">
                Back to <Link href="/login" className="text-blue-500 hover:underline">Login</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
