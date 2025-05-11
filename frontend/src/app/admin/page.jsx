"use client";

import React, { useEffect, useState } from "react";
import apiUrls from "../../backend_apis/apis"
import Cookies from 'js-cookie';
import Header from "@/components/Header";
import withAuth from "@/lib/withAuth";
import axios from "axios";
import Button from "@/components/Button";


const AdminDashboard = () => {
  const [members, setMembers] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch members from the API
  const token = Cookies.get('access_token');
 
  const fetchMembers = async () => {
    try {
      const response = await axios.get(apiUrls.get_users, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = response.data;

      if (Array.isArray(data.users)) {
        setMembers(data.users);
      } else {
        setMembers([]);
      }
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
        }
      });

      setMembers((prevMembers) =>
        Array.isArray(prevMembers) ? prevMembers.filter((member) => member.email !== email) : prevMembers
      );
    } catch (error) {
      console.error("Error removing member:", error);
    } 
  };
  
  // Filter members based on search query
  const filteredMembers = Array.isArray(members)
    ? members.filter((member) =>
        member.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];  // Return an empty array if 'members' is not an array

  // Fetch members on component mount
  useEffect(() => {
    fetchMembers();
  }, []);

  const handleactive = async (email, sub) => {

    try {
      await axios.post(apiUrls.update_subscription, 
        { subscription: sub, email }, 
        {
          headers: {
            Authorization: `Bearer ${token}`,
          }
        }
      );
  
      fetchMembers(); // Refresh members list after updating subscription
    } catch (error) {
      if (error.response) {
        console.error(error.response.data.error);
      } else {
        console.error("Error updating subscription:", error);
      }
    } 
  };
  
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <Header navItems={[{ name: "Profile", url: "/edit_profile" }]} buttons={[{ name: "Logout", url: "/login", onClick: () => Cookies.remove('access_token') }]}/>
      {/* Search Bar */}
      <div className="px-6 py-4">
        <input
          type="text"
          placeholder="Search members"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-[#1B2832] text-gray-300 py-2.5 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Table */}
      <div className="px-6 pb-8">

        {/* Add CSS for hiding columns on mobile */}
        <style jsx>{`
          @media (max-width: 800px) {
            .hide-on-mobile {
              display: none;
            }
          }
        `}</style>

        <table className="w-full text-left border-collapse overflow-hidden">
          {/* Table Header */}
          <thead className="bg-[#1B2832] text-lg">
            <tr>
              <th className="px-4 py-3 border-b border-gray-700">Name</th>
              <th className="px-4 py-3 border-b border-gray-700">Email</th>
              <th className="px-4 py-3 border-b border-gray-700">Joined</th>
              <th className="px-4 py-3 border-b border-gray-700 hide-on-mobile">Phone number</th>
              <th className="px-4 py-3 border-b border-gray-700 hide-on-mobile">Subscription</th>
              <th className="px-12 py-3 border-b border-gray-700 hide-on-mobile">Action</th>
            </tr>
          </thead>

          {/* Table Body */}
          <tbody>
            {filteredMembers.length > 0 ? (
              filteredMembers.map((member, index) => (
                <tr
                  key={index}
                  className={`${
                    index % 2 === 0 ? "bg-[#0E141B]" : "bg-[#1B2832]"
                  }`}
                >
                  <td className="px-4 py-3 border-b border-gray-700">
                    {member.name}
                  </td>
                  <td className="px-4 py-3 border-b border-gray-700">
                    {member.email}
                  </td>
                  <td className="px-4 py-3 border-b border-gray-700">
                    {member.joined}
                  </td>
                  <td className="px-4 py-3 border-b border-gray-700 hide-on-mobile">
                    {member.phone_number}
                  </td>
                  <td className="px-4 py-3 border-b border-gray-700 hide-on-mobile">
                  <Button
                    onClick={() => handleactive(member.email, member.subscription ? false : true)}
                    className="rounded-full"
                  >
                    {member.subscription ? 'Active' : 'Inactive'}
                  </Button>
                  </td>
                  <td className="px-4 py-3 border-b border-gray-700 hide-on-mobile">
                  <Button
                    onClick={() => removeMember(member.email)}
                    className="rounded-full"
                  >
                    Remove
                  </Button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="6"
                  className="text-center text-gray-400 py-4 bg-[#0E141B]"
                >
                  No members found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default withAuth(AdminDashboard);