"use client";

import { useState } from "react";
import Cookies from 'js-cookie';
import apiUrls from "../../backend_apis/apis";
import Header from "@/components/Header";
import withAuth from "@/lib/withAuth";
import axios from "axios";
import Button from "@/components/Button";

const UnSubDashboard = () => {
  const token = Cookies.get('access_token');
  const [videoFile, setVideoFile] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [classificationResult, setClassificationResult] = useState(null); // Result state

  // Handle file upload
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

    setClassificationResult(null); // Reset previous result

    const formData = new FormData();
    formData.append('video_file', videoFile);

    try {
      const response = await axios.post(apiUrls.upload_video, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
    
      const result = response.data;
      setClassificationResult(result.classification);
    } catch (error) {
      console.error('Error uploading video:', error.response.data.error);
    }
  };

  const handleDeleteVideo = () => {
    setVideoFile(null);
    setVideoPreview(null);
    setClassificationResult(null); // Clear result when deleting video
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center">
      <Header navItems={[{ name: 'Pricing', url: '/Pricing' }, { name: 'Profile', url: '/edit_profile' }]}
              buttons={[{ name: 'Logout', url: '/login', onClick: () => Cookies.remove('access_token') }]}/>

      <main className="flex flex-col items-center justify-center flex-grow space-y-8">
        <h2 className="text-3xl font-semibold text-center">
          Upload a video for activity classification
        </h2>

        <label
          htmlFor="video-upload"
          className="bg-blue-600 text-white py-2 px-4 rounded-xl hover:bg-blue-700 transition cursor-pointer"
        >
          Upload a video
        </label>
        <input
          id="video-upload"
          type="file"
          accept="video/*"
          className="hidden"
          onChange={handleVideoUpload}
        />

        {videoPreview && (
          <div className="mt-6 p-6 bg-gray-800 rounded-lg shadow-lg w-full max-w-md">
            <video
              src={videoPreview}
              controls
              className="w-full h-56 rounded-lg shadow-md"
            ></video>
            <div className="flex gap-4 mt-6 justify-between">
              <Button
                onClick={handleUploadToServer}
                className="w-full"
              >
              Submit Video
              </Button>
              <Button
                  onClick={handleDeleteVideo}
                  className="w-full"
                >
              Delete Video
              </Button>
            </div>

            {/* Classification Result */}
            {classificationResult && (
              <div className="mt-4 p-4 bg-gray-700 rounded-lg justify-center align-center">
                <p className="text-md font-semibold">
                <span className="text-white">Classification Result: </span>
                <span className="text-white">{classificationResult}</span>
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default withAuth(UnSubDashboard);