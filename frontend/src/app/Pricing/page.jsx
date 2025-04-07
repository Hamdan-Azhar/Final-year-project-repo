"use client";

import { useState } from "react";
import Cookies from 'js-cookie';
import Header from "@/components/Header";
import { useEffect } from "react";
import parseJWT from "@/lib/parseJWT";

export default function PricingPage() {
  const [current, setCurrent] = useState("Not Signed In");
  
  useEffect(() => {
    let token = Cookies.get("access_token");
    token = token ? parseJWT(token) : null;
    if (!token || token['is_admin']) {
      return;
    } else if (token['is_subscribed']) {
      setCurrent("Subscribed");
    } else {
      setCurrent("Not Subscribed");
    }

  }, []);

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-right px-4">
      {/* Header */}
      { current === "Subscribed" || current === "Not Subscribed" ? (
          <Header 
            navItems={[{ name: 'Dashboard', url: '/subdashboard' }]} 
            buttons={[{ 
              name: 'Logout', 
              url: '/login',
              onClick: () => Cookies.remove('access_token')
            }]}
          />
        ) : (
          <Header />
        )
      }
      {/* Content */}
      <main className="flex flex-col items-center">
        <h1 className="text-2xl font-inter mt-8">Upgrade to Premium</h1>
        <p className="mt-2 mb-8">Please transfer your money here: Easypaisa 0334-1111318</p>
        {/* text-gray-400 */}
        {/* Plans */}
        <div className="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-6">
          {/* Free Plan */}
          <div className="bg-[#26303B] p-6 rounded-lg w-full sm:w-80 text-center shadow-lg">
            <h2 className="text-lg font-inter mb-4">Free</h2>
            <p className="text-3xl font-inter mb-4">
              Rs0<span className="text-base font-normal">/month</span>
            </p>
            <div className={`${
                current === "Not Subscribed" ? "bg-green-500" : "bg-[#2c2c2e]"
              } rounded-full py-2 px-4 mb-4  w-fit mx-auto`}>
              {current === "Not Subscribed" ? "Current Plan" : "Select"}
            </div>
            <ul className="text-white space-y-2">
              <li>✗ No model selection</li>
              <li>✗ No cloud storage</li>
            </ul>
          </div>

          {/* Premium Plan */}
          <div className="bg-[#26303B] p-6 rounded-lg w-full sm:w-80 text-center shadow-lg">
            <h2 className="text-lg font-inter mb-4">Premium</h2>
            <p className="text-3xl font-inter mb-4">
              Rs2500<span className="text-base font-inter">/month</span>
            </p>
            <div className={`${
                current === "Subscribed" ? "bg-green-500" : "bg-[#2c2c2e]"
              } rounded-full py-2 px-4 mb-4  w-fit mx-auto`}>
              {current === "Subscribed" ? "Current Plan" : "Select"}
            </div>
            <ul className="text-white space-y-2">
              <li>✓ Advanced video analysis</li>
              <li>✓ multiple models selection</li>
              <li>✓ 50GB cloud storage</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}

