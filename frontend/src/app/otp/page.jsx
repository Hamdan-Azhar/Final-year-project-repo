"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import apiUrls from "../../backend_apis/apis";
import Header from "@/components/Header";
import Button from "@/components/Button";
import Cookies from "js-cookie";
import withAuth from "@/lib/withAuth";

const OtpPage = () => {
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(null);
  const [isExpired, setIsExpired] = useState(false);
  const router = useRouter();

  // Initialize OTP session
  useEffect(() => {
    const initializeSession = () => {
      const storedEmail = localStorage.getItem('signup_email');
      const storedExpiry = localStorage.getItem('otp_expires_at');

      if (!storedEmail || !storedExpiry) {
        router.push('/Signup');
        return;
      }

      const expiresAt = new Date(storedExpiry);
      const now = new Date();
      const remainingSeconds = Math.max(0, Math.floor((expiresAt - now) / 1000));

      setTimeLeft(remainingSeconds);
      setIsExpired(remainingSeconds <= 0);
    };

    initializeSession();
  }, [router]);

  // Countdown timer
  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          setIsExpired(true);
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (isExpired) {
      setError("OTP has expired. Please request a new one.");
      return;
    }

    setLoading(true);
    const payload = { 
      otp: otp,
      email: localStorage.getItem('signup_email') // Include email for verification
    };

    try {
      const response = await axios.post(apiUrls.otp, payload);
       // Determine redirect path based on flow type
      const flowType = localStorage.getItem('otp_flow_type');
      const redirectPath = flowType === 'password_reset' ? '/edit_profile' : '/login';
      // Clear storage on successful verification
      localStorage.removeItem('signup_email');
      localStorage.removeItem('otp_expires_at');
      localStorage.removeItem('otp_flow_type');

      if (redirectPath === '/edit_profile') {
        Cookies.set('access_token', response.data.access_token, { expires: 7 }); // Expires in 7 days
        Cookies.set("refresh_token", response.data.refresh_token, { expires: 7, secure: true });
        router.push(redirectPath);
      } else {
        router.push(redirectPath);
      }
    } catch (error) {
      if (error.response){
        const data = error.response.data;
        if (error.response.status == 429){
          setIsExpired(true);
        }
        setError(data.error);
      } else {
      setError("An error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    console.log("1")
    setLoading(true);
    setOtp(''); // Clear the OTP input field
    setError(''); // Clear any previous errors

    const email = localStorage.getItem('signup_email');
    if (!email) {
      router.push('/Signup');
      return;
    }

    try {
      const response = await axios.post(apiUrls.resend_otp, { email });
      const expiresAt = new Date();
      expiresAt.setSeconds(expiresAt.getSeconds() + response.data.otp_expires_in);
      localStorage.setItem('otp_expires_at', expiresAt.toISOString());
      // Calculate remaining time
      const now = new Date();
      const remainingSeconds = Math.max(0, Math.floor((expiresAt - now) / 1000));

      setTimeLeft(remainingSeconds);
      setIsExpired(remainingSeconds <= 0);
    } catch (error) {
      if (error.response){
        const data = error.response.data;
        setError(data.error);
      } else {
      setError("An error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    if (seconds === null) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="bg-black min-h-screen text-white">
      <Header/>
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="w-full max-w-sm text-center">
          <h2 className="text-2xl font-semibold text-white mb-8">
            OTP verification
          </h2>

          {error && (
            <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
          )}

          {!isExpired && (
            <p className={`mb-4 ${isExpired ? 'text-red-500' : 'text-blue-500'}`}>
            {`Time remaining: ${formatTime(timeLeft)}`}
          </p>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="otp" className="sr-only">
                OTP
              </label>
              <input
                id="otp"
                name="otp"
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
                disabled={isExpired}
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your OTP"
              />
            </div>
            <Button
              type="submit"
              loading={isLoading}
              disabled ={isExpired}
              className="w-full"
            >
              Verify OTP
            </Button>
          </form>
          
          {/* Resend otp link */}
          {isExpired && (
            <div className="mt-3 text-center">
              <button
                onClick={handleResendOtp}
                
                className="text-sm text-blue-500 hover:underline"
              >
                Resend OTP
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default withAuth(OtpPage);