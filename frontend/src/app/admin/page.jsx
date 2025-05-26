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

const AdminDashboard = () => {
  const [members, setMembers] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("All");
  const token = Cookies.get("access_token");
  const parsedToken = token ? parseJWT(token) : null;
  const name = parsedToken ? parsedToken.name : "";
  const role = "Admin";

  const fetchMembers = async () => {
    try {
      const response = await axios.get(apiUrls.get_users, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = response.data;
      setMembers(Array.isArray(data.users) ? data.users : []);
    } catch (error) {
      console.error("Error fetching members:", error);
      setMembers([]);
    }
  };

  const removeMember = async (email) => {
    try {
      await axios.delete(`${apiUrls.delete_user}${email}/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setMembers((prevMembers) =>
        Array.isArray(prevMembers)
          ? prevMembers.filter((member) => member.email !== email)
          : prevMembers
      );
    } catch (error) {
      console.error("Error removing member:", error);
    }
  };


  const filteredMembers = Array.isArray(members)
  ? members.filter(
      (member) =>
        member.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        (selectedLocation === "All" || member.location === selectedLocation)
    )
  : [];

    
  const uniqueLocations = Array.from(
  new Set(members.map((member) => member.location).filter(Boolean))
  );

  useEffect(() => {
    fetchMembers();
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
          { name: "Requests", url: "/requests" },
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

      {/* Search Bar */}
      <motion.div
        ref={searchRef}
        initial={{ opacity: 0, y: 20 }}
        animate={isSearchInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
        className="mb-4 max-w-6xl mx-auto px-6 pt-6"
      >
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <input
            type="text"
            placeholder="Search members"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full sm:flex-[3] border border-gray-300 rounded-lg py-2.5 px-4 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <select
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="w-full  sm:flex-[1] border border-gray-300 rounded-lg py-2.5 px-4 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Locations</option>
            {uniqueLocations.map((loc, idx) => (
              <option key={idx} value={loc}>{loc}</option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Member Table */}
      <motion.div
        ref={tableRef}
        initial={{ opacity: 0, y: 30 }}
        animate={isTableInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.7 }}
        className="overflow-x-auto px-6 pb-12 max-w-6xl mx-auto"
      >
        <style jsx>{`
          @media (max-width: 800px) {
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
              <th className="px-4 py-3 border-b border-gray-200 text-left">Joined</th>
              <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-mobile">Phone</th>
              <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-mobile">Institution</th>
              <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-mobile">Location</th>
              <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-mobile">Subscription</th>
              <th className="px-4 py-3 border-b border-gray-200 text-left hide-on-mobile">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredMembers.length > 0 ? (
              filteredMembers.map((member, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 border-b border-gray-100">{member.name}</td>
                  <td className="px-4 py-3 border-b border-gray-100">{member.email}</td>
                  <td className="px-4 py-3 border-b border-gray-100">{member.joined}</td>
                  <td className="px-4 py-3 border-b border-gray-100 hide-on-mobile">{member.phone_number}</td>
                  <td className="px-4 py-3 border-b border-gray-100">{member.institution}</td>
                  <td className="px-4 py-3 border-b border-gray-100">{member.location}</td>
                  <td className="px-4 py-3 border-b border-gray-100 hide-on-mobile">
                      {member.subscription ? "Active" : "Inactive"}
                  </td>
                  <td className="px-4 py-3 border-b border-gray-100 hide-on-mobile">
                    <Button
                      onClick={() => removeMember(member.email)}
                      className="rounded-full text-xs bg-red-400 text-red-600 hover:bg-red-600"
                    >
                      Remove
                    </Button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="text-center text-gray-500 py-6 bg-white">
                  No members found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
};

export default withAuth(AdminDashboard);