"use client";

import { useState, useEffect } from "react";
import Cookies from 'js-cookie';
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import parseJWT from "@/lib/parseJWT";
import apiUrls from "../../backend_apis/apis";

export default function PricingPage() {
  const [current, setCurrent] = useState("Not Signed In");
  const [requestSent, setRequestSent] = useState(false);
  const router = useRouter();

  useEffect(() => {
    let token = Cookies.get("access_token");
    token = token ? parseJWT(token) : null;
    if (!token || token['is_admin']) {
      return;
    }

    const checkRequestStatus = async () => {
      try {
        const response = await fetch(apiUrls.check_subscription, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${Cookies.get("access_token")}`
          }
        });
        const data = await response.json();
        if (data?.request_status === 'pending') {
          setRequestSent(true);
        }
      } catch (error) {
        console.error("Error checking subscription status:", error);
      }
    };

    if (!token) {
      setCurrent("Not Signed In");
    } else if (token['is_subscribed']) {
      setCurrent("Subscribed");
    } else {
      setCurrent("Not Subscribed");
    }

    checkRequestStatus();
  }, []);

  const handleRequest = async () => {
    const token = Cookies.get("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      const response = await fetch(apiUrls.request_subscription, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Cookies.get("access_token")}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setRequestSent(true);
      } else {
        alert(data?.error || "Failed to submit request");
      }
    } catch (error) {
      console.error("Error submitting request:", error);
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-900 flex flex-col items-center">
      {/* Header */}
      {current === "Subscribed" || current === "Not Subscribed" ? (
        <Header 
          navItems={[{ name: 'Dashboard', url: '/owner_dashboard' }]} 
          buttons={[{ 
            name: 'Logout', 
            url: '/login',
            onClick: () => Cookies.remove('access_token')
          }]}
        />
      ) : (
        <Header />
      )}

      {/* Main Content */}
      <main className="w-full max-w-4xl mt-12 px-4">
        <h1 className="text-4xl font-bold text-center mb-2">Upgrade to Premium</h1>
        <p className="text-center text-gray-600 mb-10">
          Please transfer your payment via Easypaisa (2500/month for 1 faculty dashboard): <span className="font-semibold text-gray-800">0334-1111318</span>
        </p>

        {/* Plans */}
        <div className="flex flex-col sm:flex-row justify-center gap-6">
          {/* Free Plan */}
          <div className="bg-gray-100 border border-gray-200 rounded-2xl shadow-sm p-6 w-full sm:w-80 text-center">
            <h2 className="text-xl font-semibold mb-3">Free</h2>
            <p className="text-3xl font-bold text-gray-800 mb-2">
              Rs0<span className="text-sm font-normal text-gray-600">/month</span>
            </p>
            <button
              disabled={(current === "Subscribed" && requestSent) || current === "Not Subscribed"}
              onClick={handleRequest}
              className={`rounded-full py-2 px-4 mb-4 mx-auto w-fit ${
                current === "Not Subscribed" ? "bg-green-500 text-white" : "bg-gray-200 text-gray-700"
              }`}
            >
              {current === "Subscribed"  || current === "Not Signed In" ? (requestSent ? "Requested" : "Select") : "Current Plan"}
            </button>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>✗ No faculty member dashboards</li>
              <li>✗ No model selection</li>
              <li>✗ No cloud storage</li>
            </ul>
          </div>

          {/* Premium Plan */}
          <div className="bg-white border border-gray-300 rounded-2xl shadow p-6 w-full sm:w-80 text-center">
            <h2 className="text-xl font-semibold mb-3">Premium</h2>
            <p className="text-3xl font-bold text-gray-800 mb-2">
              Rs2500<span className="text-sm font-normal text-gray-600">/month</span>
            </p>
            <button
              disabled={(current === "Not Subscribed" && requestSent) || current === "Subscribed"}
              onClick={handleRequest}
              className={`rounded-full py-2 px-4 mb-4 mx-auto w-fit ${
                current === "Subscribed" ? "bg-green-500 text-white" : "bg-gray-200 text-gray-700"
              }`}
            >
              {current === "Not Subscribed" || current === "Not Signed In" ? (requestSent ? "Requested" : "Select") : "Current Plan"}
            </button>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>✓ Faculty members dashboards for video analysis</li>
              <li>✓ Multiple models selection</li>
              <li>✓ 10GB cloud storage</li>
            </ul>
          </div>
        </div>
         {requestSent && (
            <p className="mt-6 text-center text-green-600 font-medium">
              Request submitted successfully! We will process your request soon.
            </p>
          )}
      </main>
    </div>
  );
}