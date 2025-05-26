"use client";

import React, { useEffect, useState, useRef } from "react";
import parseJWT from "@/lib/parseJWT";
import axios from "axios";
import Button from "@/components/Button";
import apiUrls from "../../backend_apis/apis";
import Header from "@/components/Header";
import { motion, useInView } from "framer-motion";
import withAuth from "@/lib/withAuth";
import Cookies from "js-cookie";


const FacultyManagementDashboard = ()  => {
  const [facultyMembers, setFacultyMembers] = useState([]);
  const [remainingSeats, setRemainingSeats] = useState(0);
  const [searchEmail, setSearchEmail] = useState("");
  const searchRef = useRef(null);
  const tableRef = useRef(null);
  const isSearchInView = useInView(searchRef, { once: true });
  const isTableInView = useInView(tableRef, { once: true });

  const token = Cookies.get("access_token");
  const parsedToken = token ? parseJWT(token) : null;
  const name = parsedToken ? parsedToken.name : "";
  const role = "Institution Owner";

  const authHeader = {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  useEffect(() => {
    fetchFacultyMembers();
  }, []);

  const fetchFacultyMembers = async () => {
    try {
      const res = await axios.get(apiUrls.get_faculty_members, authHeader);
      setFacultyMembers(res.data.faculty);
      setRemainingSeats(res.data.remaining_seats);
    } catch (err) {
      console.error("Error fetching faculty members:", err);
    }
  };

  const handleDeleteFaculty = async (email) => {
    try {
      await axios.delete(`${apiUrls.delete_faculty_member}${email}/`, authHeader);
      fetchFacultyMembers();
    } catch (err) {
      console.error("Error deleting faculty member:", err);
    }
  };

  const handleRemoveSubject = async (email, subject, timing, semester, program) => {
    try {
      await axios.delete(apiUrls.delete_faculty_member_subject, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        data: { email, subject, timing, semester, program },
      });
      fetchFacultyMembers();
    } catch (err) {
      console.error("Error removing subject:", err);
    }
  };

  const filteredFaculty = facultyMembers.filter((member) =>
    member.email.toLowerCase().includes(searchEmail.toLowerCase())
  );

  const groupedFaculty = filteredFaculty.map((member) => {
    const { faculty_member_subject, faculty_member_timing, faculty_member_program, faculty_member_semester } = member;
    const subjectInfo = (faculty_member_subject || []).map((subject, i) => ({
      subject,
      timing: faculty_member_timing?.[i] || "",
      program: faculty_member_program?.[i] || "",
      semester: faculty_member_semester?.[i] || "",
    }));
    return { ...member, subjectInfo };
  });

  return (
    <div className="min-h-screen bg-white text-gray-900">
      <Header 
      navItems={[
        { 
          name: "Assign/Add faculty", 
          url: "/assign_add_faculty" 
        },
        { 
          name: `${name} • ${role}`, 
          url: "/edit_profile" 
        }
      ]} 
      buttons={[
        {
          name: "Logout",
          url: "/login",
          onClick: () => Cookies.remove("access_token"),
        },
      ]}
      />
      {/* Search Bar + Remaining Seats Side-by-Side */}
      <motion.div
        ref={searchRef}
        initial={{ opacity: 0, y: 20 }}
        animate={isSearchInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
        className="max-w-6xl mx-auto px-6 pt-6"
      >
        <div className="flex items-center gap-4">
          {/* Search Bar (75%) */}
          <input
            placeholder="Search by email..."
            className="w-3/4 border border-gray-300 rounded-lg py-2.5 px-4 mb-6 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchEmail}
            onChange={(e) => setSearchEmail(e.target.value)}
          />

          {/* Remaining Seats (25%) */}
          <div className="w-1/4 border border-gray-300 rounded-lg py-2.5 px-4 mb-6 bg-gray-50 text-gray-900 shadow-sm text-sm">
            Remaining Seats: {remainingSeats}
          </div>
        </div>
      </motion.div>

      {/* Table */}
      <motion.div
        ref={tableRef}
        initial={{ opacity: 0, y: 30 }}
        animate={isTableInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.7 }}
        className="overflow-x-auto max-w-6xl mx-auto px-6 pb-12"
      >
        <style jsx>{`
          @media (max-width: 800px) {
            .hide-on-mobile {
              display: none;
            }
          }
        `}</style>

        <table className="min-w-full border rounded-lg overflow-hidden shadow-sm text-sm bg-white">
          <thead className="bg-gray-100 text-left">
            <tr>
              <th className="px-4 py-3 border-b">Name</th>
              <th className="px-4 py-3 border-b">Email</th>
              <th className="px-4 py-3 border-b">Phone</th>
              <th className="px-4 py-3 border-b">Password</th>
              <th className="px-4 py-3 border-b hide-on-mobile">Program</th>
              <th className="px-4 py-3 border-b hide-on-mobile">Semester</th>
              <th className="px-4 py-3 border-b hide-on-mobile">Subject</th>
              <th className="px-4 py-3 border-b hide-on-mobile">Timing</th>
              <th className="px-4 py-3 border-b hide-on-mobile">Actions</th>
            </tr>
          </thead>
          <tbody>
            {groupedFaculty.map((member, index) =>
              member.subjectInfo.length ? (
                member.subjectInfo.map((info, i) => (
                  <tr key={`${index}-${i}`} className="hover:bg-gray-50">
                    {i === 0 ? (
                      <>
                        <td className="px-4 py-3 border-b">{member.name}</td>
                        <td className="px-4 py-3 border-b">{member.email}</td>
                        <td className="px-4 py-3 border-b">{member.phone_number}</td>
                        <td className="px-4 py-3 border-b">{member.password}</td>
                      </>
                    ) : (
                      <>
                        <td className="px-4 py-3 border-b"></td>
                        <td className="px-4 py-3 border-b"></td>
                        <td className="px-4 py-3 border-b"></td>
                        <td className="px-4 py-3 border-b"></td>
                      </>
                    )}
                    <td className="px-4 py-3 border-b hide-on-mobile">{info.program}</td>
                    <td className="px-4 py-3 border-b hide-on-mobile">{info.semester}</td>
                    <td className="px-4 py-3 border-b hide-on-mobile">{info.subject}</td>
                    <td className="px-4 py-3 border-b hide-on-mobile">{info.timing}</td>
                    <td className="py-3 border-b space-x-2 space-y-6 hide-on-mobile">
                      <Button
                        variant="destructive"
                        size="sm"

                        onClick={() => handleRemoveSubject(member.email, info.subject, info.timing, info.semester, info.program)}
                      >
                        Remove Subject
                      </Button>
                      {i === 0 && (
                        <Button
                          variant="danger"
                          className="rounded-full bg-red-400 text-red-600 hover:bg-red-600 hide-on-mobile"
                          onClick={() => handleDeleteFaculty(member.email)}
                        >
                          Delete User
                        </Button>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 border-b">{member.name}</td>
                  <td className="px-4 py-3 border-b">{member.email}</td>
                  <td className="px-4 py-3 border-b">{member.phone_number}</td>
                  <td colSpan={4} className="px-4 py-3 border-b text-gray-500">
                    No subjects assigned
                  </td>
                  <td className="px-4 py-3 border-b">
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDeleteFaculty(member.email)}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              )
            )}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}

export default withAuth(FacultyManagementDashboard);
