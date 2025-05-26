"use client";

import React, { useState, useEffect } from "react";
import parseJWT from "@/lib/parseJWT";
import apiUrls from "../../backend_apis/apis";
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import withAuth from "@/lib/withAuth";
import Header from "@/components/Header";
import Button from "@/components/Button";
import axios from "axios";
import { motion } from "framer-motion";

const FacultyDashboard = () => {
  const [storage, setStorage] = useState({ used: "0.00 GB", remaining: "10.00 GB", total: "10 GB" });
  const [videos, setVideos] = useState([]);
  const [selectedModel, setSelectedModel] = useState("Deep Learning Model");
  const [subjectChoices, setSubjectChoices] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState("");
  const [selectedExamType, setSelectedExamType] = useState("Quiz");
  const token = Cookies.get('access_token');
  const parsedToken = token ? parseJWT(token) : null;
  const name = parsedToken ? parsedToken.name : "";
  const role = "Faculty";
  const router = useRouter();
  const [videoFile, setVideoFile] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [classificationResult, setClassificationResult] = useState(null);

  const fetchData = async () => {
    try {
      const response = await axios.get(apiUrls.get_videos, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = response.data;
      setStorage(data.cloud_storage);
      // setStorage({ used: "7.00 GB", remaining: "10.00 GB", total: "10 GB" })
      setVideos(data.videos);
      console.log("videos", data.videos);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const fetchSubjects = async () => {
    try {
      const response = await axios.get(apiUrls.get_faculty_member, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const subjects = response.data.faculty_data?.faculty_member_subject || [];
      setSubjectChoices(subjects);
      console.log("subjects", subjects);
      if (subjects.length > 0) {
        setSelectedSubject(subjects[0]); // default selection
      }
      console.log("Type:", typeof selectedSubject);
      console.log("Selected Choices:", typeof subjectChoices);
      // console.log("Subject:", subjects);
    } catch (error) {
      console.error("Error fetching subjects:", error);
    }
  };

  useEffect(() => { fetchData(); fetchSubjects(); }, []);

  const handleDeleteVideo = async (name) => {
    try {
      await axios.delete(`${apiUrls.delete_video}${name}/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setVideos(videos.filter(video => video.name !== name));
    } catch (error) {
      console.error("Error deleting video:", error);
    }
  };

  const handleClickVideo = (assetId) => {
    router.push(`/video?videoName=${assetId}`);
  };

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setVideoFile(file);
      setVideoPreview(URL.createObjectURL(file));
    }
    event.target.value = '';
  };

  const handleUploadToServer = async () => {
    if (!videoFile) {
      alert('Please upload a video first.');
      return;
    }

    setClassificationResult(null);
    const formData = new FormData();
    formData.append('video_file', videoFile);
    formData.append('model_type', selectedModel);
    formData.append('subject', selectedSubject);
    formData.append('exam_type', selectedExamType);


    try {
      const response = await axios.post(apiUrls.upload_video, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      setClassificationResult(response.data.classification);
      fetchData();
    } catch (error) {
      console.error('Error uploading video:', error);
    }
  };

  const handleDeleteVideoPreview = () => {
    setVideoFile(null);
    setVideoPreview(null);
    setClassificationResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Header
        navItems={[
          { name: `${name} • ${role}`, url: "/edit_profile" },
        ]}
        buttons={[
          {
            name: 'Logout',
            url: '/login',
            onClick: () => Cookies.remove('access_token')
          }
        ]}
      />

      <motion.main
        className="max-w-5xl mx-auto px-6 py-12"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="text-3xl font-bold mb-8">Dashboard</h2>

        <div className="mb-8">
          <label className="block text-lg font-medium mb-2">Selected AI Model</label>
          <select
            className="w-full bg-white text-gray-900 p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option>Deep Learning Model</option>
            <option>Machine Learning Model</option>
          </select>
        </div>

        <motion.div
          className="mb-10"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
        >
          <label className="block text-lg font-medium mb-2">Cloud Storage</label>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="text-sm mb-2">{storage.used} used</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-purple-600 h-2 rounded-full"
                style={{ width: `${(parseFloat(storage.used) / parseFloat(storage.total)) * 100}%` }}
              ></div>
            </div>
            <div className="text-sm mt-2">{storage.remaining} remaining</div>
          </div>
        </motion.div>

        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
        >
          <label className="block text-lg font-medium mb-4">Video Uploads</label>
          <div className="overflow-x-auto bg-white rounded-lg border border-gray-200 shadow-sm">
            <style jsx>{`
              @media (max-width: 800px) {
                .hide-on-mobile {
                  display: none;
                }
              }
            `}</style>
            <table className="w-full table-auto text-left">
              <thead className="bg-gray-100">
                <tr>
                  <th className="py-3 px-4 text-sm font-semibold">Video Name</th>
                  <th className="py-3 px-4 text-sm font-semibold">Subject</th>
                  <th className="py-3 px-4 text-sm font-semibold">Exam Type</th>
                  <th className="py-3 px-4 text-sm font-semibold">Program</th>
                  <th className="py-3 px-4 text-sm font-semibold hide-on-mobile">Semester</th>
                  <th className="py-3 px-4 text-sm font-semibold hide-on-mobile">Timing</th>
                  <th className="py-3 px-4 text-sm font-semibold hide-on-mobile">Storage</th>
                  <th className="py-3 px-4 text-sm font-semibold hide-on-mobile">Action</th>
                </tr>
              </thead>
              <tbody>
                {videos.map((video, index) => (
                  <motion.tr
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className="border-t"
                  >
                    <td
                      className="py-3 px-4 cursor-pointer text-indigo-600 hover:underline"
                      onClick={() => handleClickVideo(video.name)}
                    >
                      {video.name}
                    </td>
                    <td className="py-3 px-4">{video.subject}</td>
                    <td className="py-3 px-4">{video.exam_type}</td>
                    <td className="py-3 px-4">{video.program}</td>
                    <td className="py-3 px-4 hide-on-mobile">{video.semester}</td>
                    <td className="py-3 px-4 hide-on-mobile">{video.timing}</td>
                    <td className="py-3 px-4 hide-on-mobile">{video.size}</td>
                    <td className="py-3 px-4 hide-on-mobile">
                      <Button onClick={() => handleDeleteVideo(video.name)}>Delete</Button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        <div className="text-center">
          <label htmlFor="video-upload" className="cursor-pointer inline-block bg-purple-600 text-white py-2 px-6 rounded-xl hover:bg-purple-700 transition">
            Upload a video
          </label>
          <input
            id="video-upload"
            type="file"
            accept="video/*"
            className="hidden"
            onChange={handleVideoUpload}
          />
        </div>

        {videoPreview && (
          <motion.div
            className="mt-10 bg-white rounded-xl p-6 shadow-md max-w-md mx-auto"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
          >
            <video src={videoPreview} controls className="w-full h-56 rounded-lg mb-4" />
            <div className="mb-4">
              <label className="block text-md font-medium text-gray-900 mb-1">Select Subject</label>
              <select
                className="w-full p-2 border rounded-md rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
              >
                {subjectChoices.map((subject, index) => (
                  <option key={index} value={subject}>{subject}</option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-md font-medium text-gray-900 mb-1">Select Exam Type</label>
              <select
                className="w-full p-2 border rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={selectedExamType}
                onChange={(e) => setSelectedExamType(e.target.value)}
              >
                <option value="Quiz">Quiz</option>
                <option value="Mid Exam">Mid Exam</option>
                <option value="Final Exam">Final Exam</option>
              </select>
            </div>

            <div className="flex gap-4">
              <Button onClick={handleUploadToServer} className="w-full">Submit Video</Button>
              <Button onClick={handleDeleteVideoPreview} className="w-full">Delete Video</Button>
            </div>

             {classificationResult && (
              <a
                href={classificationResult}
                download
                target="_blank"
                rel="noopener noreferrer"
                className="block mt-4"
              >
                <Button className="w-full">Download Classification Report</Button>
              </a>
            )}
          </motion.div>
        )}
      </motion.main>
    </div>
  );
};

export default withAuth(FacultyDashboard);