"use client";

import React, { useEffect, useState } from "react";
import parseJWT from "@/lib/parseJWT";
import axios from "axios";
import Cookies from "js-cookie";
import apiUrls from "../../backend_apis/apis";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Label,
  PieChart, Pie, Cell, Legend,
  BarChart, Bar,
} from "recharts";
import Header from "@/components/Header";
import withAuth from "@/lib/withAuth";
import { motion } from "framer-motion"; // Import framer-motion for animations

const COLORS = ["#00C49F", "#FF8042"];
const modelColors = {
  "Deep Learning Model": "#8884d8",
  "Machine Learning Model": "#82ca9d"
};

const AdminChartsDashboard = () => {
  const [userData, setUserData] = useState([]);
  const [videoData, setVideoData] = useState([]);
  const [userTimeRange, setUserTimeRange] = useState("7d");
  const [modelTimeRange, setModelTimeRange] = useState("7d");
  const [pieTimeRange, setPieTimeRange] = useState("7d");

  const token = Cookies.get("access_token");
  const parsedToken = token ? parseJWT(token) : null;
  const name = parsedToken ? parsedToken.name : "";
  const role = "Admin";

  const fetchData = async () => {
    try {
      const [usersRes, videosRes] = await Promise.all([
        axios.get(apiUrls.get_users, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(apiUrls.get_all_videos, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setUserData(Array.isArray(usersRes.data.users) ? usersRes.data.users : []);
      setVideoData(Array.isArray(videosRes.data.videos) ? videosRes.data.videos : []);
    } catch (err) {
      console.error("Failed to fetch dashboard data", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const generateDateRange = (days) => {
    const today = new Date();
    const range = [];
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      range.push(date.toISOString().split("T")[0]);
    }
    return range;
  };

  const getDaysFromRange = (range) => {
    const map = { "7d": 7, "14d": 14, "1m": 30, "6m": 180 };
    return map[range];
  };

  const getCumulativeUserData = () => {
    const dateRange = generateDateRange(getDaysFromRange(userTimeRange));
    let cumulative = 0;
    const joinCounts = userData.reduce((acc, user) => {
      const date = new Date(user.joined).toISOString().split("T")[0];
      acc[date] = (acc[date] || 0) + 1;
      return acc;
    }, {});
    return dateRange.map(date => {
      cumulative += joinCounts[date] || 0;
      return { date, count: cumulative };
    });
  };

  const getModelUsageData = () => {
    const dateRange = generateDateRange(getDaysFromRange(modelTimeRange));
    const usageCounts = videoData.reduce((acc, v) => {
      const date = v.date;
      if (!acc[date]) acc[date] = { "Deep Learning Model": 0, "Machine Learning Model": 0 };
      acc[date][v.model_type] += 1;
      return acc;
    }, {});
    return dateRange.map(date => ({
      date,
      "Deep Learning Model": usageCounts[date]?.["Deep Learning Model"] || 0,
      "Machine Learning Model": usageCounts[date]?.["Machine Learning Model"] || 0,
    }));
  };

  const getPieChartData = () => {
    const days = getDaysFromRange(pieTimeRange);
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    const filteredUsers = userData.filter(u => new Date(u.joined) >= cutoffDate);
    const activeCount = filteredUsers.filter(u => u.subscription).length;
    const inactiveCount = filteredUsers.length - activeCount;
    return [
      { name: "Active", value: filteredUsers.length ? (activeCount / filteredUsers.length * 100) : 0 },
      { name: "Inactive", value: filteredUsers.length ? (inactiveCount / filteredUsers.length * 100) : 0 },
    ];
  };

  return (
    <div className="min-h-screen bg-white text-gray-900">
      <Header navItems={[
        { name: "Users", url: "/admin" }, 
        { name: "Requests", url: "/requests" }, 
        { name: `${name} • ${role}`, url: "/edit_profile" }
      ]} 
      buttons={[
        { name: "Logout", url: "/login", 
        onClick: () => Cookies.remove('access_token') 
      }]} />

      <motion.div className="text-gray-800 px-6 py-8 max-w-5xl mx-auto">
        <div className="flex justify-end mb-4">
          <select
            value={userTimeRange}
            onChange={(e) => setUserTimeRange(e.target.value)}
            className="border px-3 py-1 rounded-md"
          >
            <option value="7d">Last 7 Days</option>
            <option value="14d">Last 2 Weeks</option>
            <option value="1m">Last 1 Month</option>
            <option value="6m">Last 6 Months</option>
          </select>
        </div>

        {/* Line Chart for User Growth */}
        <motion.div
          initial={{ opacity: 0, y: 100 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-semibold mb-6 text-center">User Growth Over Time</h2>
          <div className="bg-white rounded-2xl p-5 shadow-md border border-gray-200">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={getCumulativeUserData()} margin={{ top: 15, right: 0, left: 15, bottom: 35 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#4a5568">
                  <Label value="Date" position="bottom" offset={20} style={{ textAnchor: 'middle' }} />
                </XAxis>
                <YAxis stroke="#4a5568">
                  <Label value="User Count" position="left" angle={-90} style={{ textAnchor: 'middle' }} />
                </YAxis>
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#800080" strokeWidth={2} dot={{ r: 4 }} isAnimationActive={true} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Pie Chart for Subscription Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 100 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="mb-12"
        >
          <div className="flex justify-end mb-4">
            <select
              value={pieTimeRange}
              onChange={(e) => setPieTimeRange(e.target.value)}
              className="border px-3 py-1 rounded-md"
            >
              <option value="7d">Last 7 Days</option>
              <option value="14d">Last 2 Weeks</option>
              <option value="1m">Last 1 Month</option>
              <option value="6m">Last 6 Months</option>
            </select>
          </div>

          <h2 className="text-3xl font-semibold mb-6 text-center">Subscription Breakdown</h2>
          <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-200 flex justify-center">
            <ResponsiveContainer width="60%" height={300}>
              <PieChart>
                <Pie data={getPieChartData()} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={(entry) => `${(entry.value).toFixed(0)}%`} isAnimationActive>
                  {getPieChartData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Bar Chart for Model Usage */}
        <motion.div
          initial={{ opacity: 0, y: 100 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="mb-12"
        >
          <div className="flex justify-end mb-4">
            <select
              value={modelTimeRange}
              onChange={(e) => setModelTimeRange(e.target.value)}
              className="border px-3 py-1 rounded-md"
            >
              <option value="7d">Last 7 Days</option>
              <option value="14d">Last 2 Weeks</option>
              <option value="1m">Last 1 Month</option>
              <option value="6m">Last 6 Months</option>
            </select>
          </div>

          <h2 className="text-3xl font-semibold mb-6 text-center">Model Usage Frequency</h2>
          <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-200">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={getModelUsageData()} margin={{ top: 0, right: 0, left: 15, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#4a5568">
                  <Label value="Date" position="bottom" offset={55} style={{ textAnchor: 'middle' }} />
                </XAxis>
                <YAxis stroke="#4a5568">
                  <Label value="Usage Count" position="left" angle={-90} style={{ textAnchor: 'middle' }} />
                </YAxis>
                <Tooltip />
                <Legend 
                  verticalAlign="bottom" 
                  wrapperStyle={{ transform: "translateY(10px)" }} 
                />
                <Bar dataKey="Deep Learning Model" stackId="a" fill={modelColors["Deep Learning Model"]} isAnimationActive />
                <Bar dataKey="Machine Learning Model" stackId="a" fill={modelColors["Machine Learning Model"]} isAnimationActive />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default withAuth(AdminChartsDashboard);
