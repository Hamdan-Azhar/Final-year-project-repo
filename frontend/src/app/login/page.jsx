"use client";

import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import apiUrls from "../../backend_apis/apis";
import Cookies from 'js-cookie';
import Link from 'next/link';
import Header from "@/components/Header";
import Button from "@/components/Button";


export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const payload = {
      email: email,
      password: password,
    };

    try {
      const response = await axios.post(apiUrls.login, payload);
      Cookies.set('access_token', response.data.access_token, { expires: 7 }); // Expires in 7 days
      Cookies.set("refresh_token", response.data.refresh_token, { expires: 7, secure: true });

      const redirectPath = response.data.admin === "True" ? "/admin" : 
      response.data.subscription === "True" ? "/subdashboard" : "/unsubdashboard";
  
      if (response?.data?.admin === "True") {
        router.push(redirectPath);
      } else if (response?.data?.subscription === "True") {
        router.push(redirectPath);
      } else {
        router.push(redirectPath);
      }
    } catch (error) {
      if (error.response){
        if (error.response.data.needs_verification) {
            router.push("/forget");  // Redirect to verification page
        } else {
            setError(error.response.data.error);
        }
      } else{
        setError("An error occured in login. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-black min-h-screen text-white">
      {/* Header */}
      <Header/>
      {/* Main Form */}
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="w-full max-w-sm text-center">
          <h2 className="text-2xl font-semibold text-white mb-8">
            Log in to ExamGuard
          </h2>

           {/* Error Message */}
           {error && (
            <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            {/* Email Field */}
            <div className="mb-4">
              <input
                type="email"
                id="email"
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            {/* Password Field with Show/Hide */}
            <div className="mb-4">
              <input
                type="password"
                id="confirm-password"
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Forgot Password Link */}
            <div className="text-right mb-2">
              <Link href="/forget" className="text-sm text-blue-500 hover:underline">
                Forgot your password?
              </Link>
            </div>

            {/* Login Button */}
            <Button
                type="submit"
                loading={isLoading}
                className="w-full"
              >
                Login
            </Button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">Don&apos;t have an account?</p>
            <Link href="/Signup" className="text-sm text-blue-500 hover:underline">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
