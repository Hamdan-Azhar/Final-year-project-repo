"use client";

import React, { useEffect, useState, useRef } from "react";
import parseJWT from "@/lib/parseJWT";
import apiUrls from "../../backend_apis/apis";
import Cookies from "js-cookie";
import Header from "@/components/Header";
import withAuth from "@/lib/withAuth";
import axios from "axios";
import Button from "@/components/Button";
import { motion, useInView } from "framer-motion";

const SubscriptionRequests = () => {
  const [requests, setRequests] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");

  const token = Cookies.get("access_token");
  const parsedToken = token ? parseJWT(token) : null;
  const name = parsedToken ? parsedToken.name : "";
  const role = "Admin";

  const fetchRequests = async () => {
    try {
      const response = await axios.get(apiUrls.get_all_requests, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = response.data.requests || [];
      const sortedData = data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      setRequests(sortedData);
    } catch (error) {
      console.error("Error fetching requests:", error);
      setRequests([]);
    }
  };


  const handleRequestAction = async (email, action) => {
    try {
      await axios.post(
        apiUrls.update_subscription,
        { action, email },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      fetchRequests();
    } catch (error) {
      console.error("Error updating request:", error);
    }
  };

  const filteredRequests = Array.isArray(requests)
    ? requests.filter((req) => {
        const dateTime = new Date(req.timestamp);
        const dateStr = dateTime.toISOString().split("T")[0];
        return selectedDate ? dateStr === selectedDate : true;
      })
    : [];

  useEffect(() => {
    fetchRequests();
  }, []);

  const searchRef = useRef(null);
  const tableRef = useRef(null);
  const isSearchInView = useInView(searchRef, { once: true });
  const isTableInView = useInView(tableRef, { once: true });

  return (
    <div className="min-h-screen bg-white text-gray-900">
      <Header
        navItems={[
          { name: "Analytics", url: "/analytics" },
          { name: "Users", url: "/admin" },
          { name: `${name} • ${role}`, url: "/edit_profile" },
        ]}
        buttons={[
          {
            name: "Logout",
            url: "/login",
            onClick: () => Cookies.remove("access_token"),
          },
        ]}
      />

      <div className="max-w-6xl mx-auto px-6 pt-6">
        <motion.div
          ref={searchRef}
          initial={{ opacity: 0, y: 20 }}
          animate={isSearchInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="mb-4"
        >
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full border border-gray-300 rounded-lg py-2.5 px-4 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </motion.div>

        <motion.div
          ref={tableRef}
          initial={{ opacity: 0, y: 30 }}
          animate={isTableInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="overflow-x-auto pb-12"
        >
          <style jsx>{`
            @media (max-width: 900px) {
              .hide-on-tablet {
                display: none;
              }
            }
            @media (max-width: 500px) {
              .hide-on-mobile {
                display: none;
              }
            }
          `}</style>

          <table className="min-w-full bg-white border rounded-lg overflow-hidden shadow-sm text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-3 border-b border-gray-200 text-left">Name</th>
                <th className="px-4 py-3 border-b border-gray-200 text-left">Email</th>
                <th className="px-4 py-3 border-b border-gray-200 text-left">Phone</th>
                <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-mobile">Request Type</th>
                <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-mobile">Date</th>
                <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-tablet">Time</th>
                <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-tablet">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRequests.length > 0 ? (
                filteredRequests.map((req, index) => {
                  const dateTime = new Date(req.timestamp);
                  const date = dateTime.toLocaleDateString();
                  const time = dateTime.toLocaleTimeString();
                  return (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 border-b border-gray-100">{req.name}</td>
                      <td className="px-4 py-3 border-b border-gray-100">{req.email}</td>
                      <td className="px-4 py-3 border-b border-gray-100">{req.phone_number}</td>
                      <td className="px-4 py-3 border-b border-gray-100 hide-on-mobile">{req.action}</td>
                      <td className="px-4 py-3 border-b border-gray-100 hide-on-mobile">{date}</td>
                      <td className="px-4 py-3 border-b border-gray-100 hide-on-tablet">{time}</td>
                      <td className="px-4 py-3 border-b border-gray-100 hide-on-tablet">
                        <div className="flex space-x-2">
                          <Button onClick={() => handleRequestAction(req.email, "approve")} className="rounded-full text-xs bg-green-400 hover:bg-green-500 text-white">
                            Approve
                          </Button>
                          <Button onClick={() => handleRequestAction(req.email, "reject")} className="rounded-full text-xs bg-red-400 hover:bg-red-500 text-white">
                            Reject
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="7" className="text-center text-gray-500 py-6 bg-white">
                    No requests found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </motion.div>
      </div>
    </div>
  );
};

export default withAuth(SubscriptionRequests);
