"use client";

import React, { useState, useRef } from "react";
import parseJWT from "@/lib/parseJWT";
import axios from "axios";
import Button from "@/components/Button";
import apiUrls from "../../backend_apis/apis";
import Header from "@/components/Header";
import { motion, useInView } from "framer-motion";
import withAuth from "@/lib/withAuth";
import Cookies from "js-cookie";


const AssignAddFacultyPage = ()  => {
  const [error, setError] = useState("");
  const [error2, setError2] = useState("");
  const [success, setSuccess] = useState("");
  const [success2, setSuccess2] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
    phoneNo: "",
  });

  const [subjectForm, setSubjectForm] = useState({
    email: "",
    program: "",
    semester: "",
    subject: "",
    timing: "",
  });

  const tableRef = useRef(null);
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

  const handleCreateFaculty = async (e) => {
    e.preventDefault();
    setIsLoading(true);
  
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,20}$/;
    if (!passwordRegex.test(formData.password)) {
      setError(
        "Password must be 8-20 characters long, with at least: " +
        "1 uppercase letter, 1 lowercase letter, and 1 number."
      );
      setIsLoading(false);
      return;
    }
  
    if (formData.password !== formData.confirm_password) {
      setError("Password and Confirm Password do not match.😊");
      setIsLoading(false);
      return;
    }
  
    const phoneRegex = /^(\+92|0092|0)?(3\d{2})(\d{7})$/;
    if (!phoneRegex.test(formData.phoneNo)) {
      setError("Please enter a valid Pakistan phone number.😊");
      setIsLoading(false);
      return;
    }

    setError("");
  
    try {
      await axios.post(apiUrls.create_faculty_member, formData, authHeader);
      setFormData({ name: "", email: "", password: "", confirm_password: "", phoneNo: "" });
      setSuccess(`Faculty member created successfully!. Check the ${formData.email} for the login credentials.`);
    } catch (err) {
      setError(err.response.data.error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddSubject = async () => {

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(subjectForm.email)) {
      setError2("Please enter a valid email address.");
      return;
    }

    // Timing format: 24-hour format HH:MM
    const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/;
    if (!timeRegex.test(subjectForm.timing)) {
      setError2("Timing must be in 24-hour format (e.g., 14:00, 09:30).");
      return;
    }

    // Semester must be integer 1–8
    const semesterNum = parseInt(subjectForm.semester, 10);
    if (isNaN(semesterNum) || semesterNum < 1 || semesterNum > 8) {
      setError2("Semester must be an integer between 1 and 8.");
      return;
    }

    setError2("");

    try {
      await axios.post(apiUrls.create_faculty_member_subject, subjectForm, authHeader);
      setSuccess2(`Subject assigned to Faculty member successfully!`);
    } catch (err) {
      setError2(err.response.data.error);
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-900">
      <Header
      navItems={[
        {
          name: "Dashboard",
          url: "/owner_dashboard",
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
      <motion.div
        ref={tableRef}
        initial={{ opacity: 0, y: 30 }}
        animate={isTableInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.7 }}
        className="max-w-3xl mx-auto px-6 pb-8"
      >
      {/* Create Faculty Form */}
        <div className="bg-white shadow-md p-4 rounded-lg mb-6 border border-gray-200">
          <h2 className="text-2xl font-semibold mb-6 text-center">Add New Faculty Member</h2>
          {error && (
            <p className="text-red-500 text-sm text-center mb-4">{error}</p>
          )}
          {success && (
            <p className="text-green-500 text-sm text-center mb-4">{success}</p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.keys(formData).map((key) => {
              let type = "text";
              if (key === "email") type = "email";
              else if (key === "password" || key === "confirm_password") type = "password";
              else if (key === "phoneNo") type = "tel";

              return (
                <input
                  key={key}
                  type={type}
                  className="border border-gray-300 p-2 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder={key.replace("_", " ")}
                  value={formData[key]}
                  onChange={(e) => setFormData({ ...formData, [key]: e.target.value })}
                />
              );
            })}
          </div>
          <Button onClick={handleCreateFaculty} loading={isLoading} className="mt-4 w-full py-2">Create Faculty</Button>
        </div>

        {/* Assign Subject Form */}
        <div className="bg-white shadow-md p-4 rounded-lg border border-gray-200">
          <h3 className="text-2xl font-semibold mb-6 text-center">Assign Subject</h3>
          {error2 && (
            <p className="text-red-500 text-sm text-center mb-4">{error2}</p>
          )}
           {success2 && (
            <p className="text-green-500 text-sm text-center mb-4">{success2}</p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.keys(subjectForm).map((key) => (
              <input
                key={key}
                className="border border-gray-300 p-2 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder={key}
                value={subjectForm[key]}
                onChange={(e) => setSubjectForm({ ...subjectForm, [key]: e.target.value })}
              />
            ))}
          </div>
          <Button onClick={handleAddSubject} className="mt-4 w-full py-2">Assign Subject</Button>
        </div>
      </motion.div>
    </div>
  );
}

export default withAuth(AssignAddFacultyPage);
