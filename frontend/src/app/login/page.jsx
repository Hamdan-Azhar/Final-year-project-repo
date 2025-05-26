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
    const payload = { email, password };

    try {
      const response = await axios.post(apiUrls.login, payload);
      Cookies.set('access_token', response.data.access_token, { expires: 7 });
      Cookies.set("refresh_token", response.data.refresh_token, { expires: 7, secure: true });

      const redirectPath =
        response.data.admin === "True"
          ? "/admin"
          : response.data.subscription === "True"
          ? "/owner_dashboard"
          : response.data.faculty === "True"
          ? "/faculty_dashboard"
          : "/unsubdashboard";

      router.push(redirectPath);
    } catch (error) {
      if (error.response) {
        if (error.response.data.needs_verification) {
          router.push("/forget");
        } else {
          setError(error.response.data.error);
        }
      } else {
        setError("An error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white min-h-screen text-gray-900">
      {/* Header */}
      <Header />

      {/* Login Form */}
      <div className="flex items-center justify-center px-6 py-20">
        <div className="w-full max-w-md">
          <h2 className="text-3xl font-bold text-center mb-8">
            Log in to <span className="text-purple-600">ExamGuard</span>
          </h2>

          {/* Error */}
          {error && (
            <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <input
              type="email"
              placeholder="Email address"
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            {/* Password */}
            <input
              type="password"
              placeholder="Password"
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            {/* Forgot Password */}
            <div className="text-right text-sm">
              <Link href="/forget" className="text-indigo-600 hover:underline">
                Forgot your password?
              </Link>
            </div>

            {/* Login Button */}
            <Button type="submit" loading={isLoading} className="w-full">
              Login
            </Button>
          </form>

          {/* Sign Up */}
          <div className="mt-6 text-center text-sm text-gray-600">
            Don&apos;t have an account?{" "}
            <Link href="/Signup" className="text-indigo-600 hover:underline">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
