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
  const [location, setLocation] = useState("Karachi");
  const [userType, setUserType] = useState("user"); // default to 'user'
  const [isChecked, setIsChecked] = useState(false);
  const [institution, setInstitution] = useState("institute");
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
      institution: institution,
      location: location,
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
    <div className="bg-white min-h-screen text-gray-900" >
      {/* Header */}
      <Header/>
      
      {/* Login Form */}
      <div className="flex items-center justify-center px-6 py-20">
        <div className="w-full max-w-md">
          <h2 className="text-3xl font-bold text-center mb-8">
            Create an account
          </h2>

          {/* Error */}
          {error && (
            <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">

            {/* Username */}
            <input
              type="text"
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            {/* Email */}
            <input
              type="email"
              placeholder="Email address"
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

             {/* Institution */}
            { userType !== "admin" && <input
              type="text"
              onChange={(e) => setInstitution(e.target.value)}
              placeholder="Enter your institution name"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            /> }

            {/* Location */}
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="Karachi">Karachi</option>
              <option value="Lahore">Lahore</option>
              <option value="Islamabad">Islamabad</option>
              <option value="Rawalpindi">Rawalpindi</option>
              <option value="Peshawar">Peshawar</option>
              <option value="Quetta">Quetta</option>
            </select>


            {/* Password */}
            <input
              type="password"
              placeholder="Password"
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            {/* Confirm Password */}
            <input
              type="password"
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm password"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            
            {/* Phone Number */}
            <input
              type="tel"
              id="tel"
              onChange={(e) => setPhoneNo(e.target.value)}
              placeholder="Type your phone number"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            {/* User Type */}
            <select
              value={userType}
              onChange={(e) => setUserType(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>

            {/* Check box */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="terms"
                checked={isChecked}
                onChange={() => setIsChecked(!isChecked)}
                className="text-blue-500 mr-2"
              />
              <label htmlFor="terms" className="text-sm text-gray-600">
                I agree to the Terms of Service and Privacy Policy
              </label>
            </div>

            {/* Signup Button */}
            <Button type="submit" loading={isLoading} className="w-full">
              Sign up
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
