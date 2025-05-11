"use client";

import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import apiUrls from "../../backend_apis/apis";
import Header from "@/components/Header";
import Button from "@/components/Button";

export default function SignupPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [confirmpassword, setConfirmPassword] = useState("");
  const [phoneNo, setPhoneNo] = useState("");
  const [userType, setUserType] = useState("user"); // default to 'user'
  const [isChecked, setIsChecked] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false); 
  const router = useRouter();


  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
  
    // Validations remain the same
    if (!isChecked) {
      setError("Please tick the checkbox to agree to the terms.😊");
      setIsLoading(false);
      return;
    }
  
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,20}$/;
    if (!passwordRegex.test(password)) {
      setError(
        "Password must be 8-20 characters long, with at least: " +
        "1 uppercase letter, 1 lowercase letter, and 1 number."
      );
      setIsLoading(false);
      return;
    }
  
    if (password !== confirmpassword) {
      setError("Password and Confirm Password do not match.😊");
      setIsLoading(false);
      return;
    }
  
    const phoneRegex = /^(\+92|0092|0)?(3\d{2})(\d{7})$/;
    if (!phoneRegex.test(phoneNo)) {
      setError("Please enter a valid Pakistan phone number.😊");
      setIsLoading(false);
      return;
    }
  
    setError("");
  
    const payload = {
      name: username,
      password: password,
      confirm_password: confirmpassword,
      email: email,
      phoneNo: phoneNo,
      role: userType,
    };
  
    try {
      const response = await axios.post(apiUrls.signup, payload);
      // Store email in localStorage before redirect
      localStorage.setItem('signup_email', email);
      
      // Store expiration time if available in response
      if (response.data.otp_expires_in) {
        const expiresAt = new Date();
        expiresAt.setSeconds(expiresAt.getSeconds() + response.data.otp_expires_in);
        localStorage.setItem('otp_expires_at', expiresAt.toISOString());
      }
      // Redirect to OTP page
      router.push('/otp');
    } catch (error) {
      if (error.response){
        const data = error.response.data;
        setError(data.error);
      } else {
      // Clear any stored OTP data if signup fails
      localStorage.removeItem('signup_email');
      localStorage.removeItem('otp_expires_at');
      setError("An error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-black min-h-screen text-white" >
      {/* Header */}
      <Header/>
      {/* Main Form */}
      <div className="flex items-center justify-center py-12">
        <div className="w-full max-w-sm text-center">
          <h2 className="text-2xl font-semibold text-white text-center mb-6">
            Create an account
          </h2>

          {/* Error Message */}
          {error && (
            <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <input
                type="email"
                id="email"
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mb-4">
              <input
                type="text"
                id="username"
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mb-4">
              <input
                type="password"
                id="password"
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mb-4">
              <input
                type="password"
                id="confirm-password"
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm password"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mb-4">
              <input
                type="tel"
                id="tel"
                onChange={(e) => setPhoneNo(e.target.value)}
                placeholder="Type your phone number"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mb-4">
              <select
                value={userType}
                onChange={(e) => setUserType(e.target.value)}
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div className="flex items-center mb-6">
              <input
                type="checkbox"
                id="terms"
                checked={isChecked}
                onChange={() => setIsChecked(!isChecked)}
                className="text-blue-500 mr-2"
              />
              <label htmlFor="terms" className="text-sm font-inter">
                I agree to the Terms of Service and Privacy Policy
              </label>
            </div>
            <Button
              type="submit"
              loading={isLoading}
              className="w-full"
            >
              Sign up
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
