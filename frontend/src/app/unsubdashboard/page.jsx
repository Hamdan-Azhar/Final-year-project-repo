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
    <div className="min-h-screen bg-white text-gray-900 flex flex-col items-center">
      <Header navItems={[{ name: 'Pricing', url: '/Pricing' }, { name: 'Profile', url: '/edit_profile' }]}
              buttons={[{ name: 'Logout', url: '/login', onClick: () => Cookies.remove('access_token') }]}/>

      <main className="flex flex-col items-center justify-center flex-grow space-y-8">
        <h2 className="text-3xl font-semibold text-center">
          Upload a video for activity classification
        </h2>

        <label
          htmlFor="video-upload"
          className="bg-purple-600 text-white py-2 px-4 rounded-xl hover:bg-purple-700 transition cursor-pointer"
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

        {/* Preview & Submit */}
        {videoPreview && (
          <div className="mt-10 bg-white rounded-xl p-6 shadow-md max-w-md mx-auto">
            <video src={videoPreview} controls className="w-full h-56 rounded-lg mb-4" />
            <div className="flex gap-4">
              <Button onClick={handleUploadToServer} className="w-full">Submit Video</Button>
              <Button onClick={handleDeleteVideo} className="w-full">Delete Video</Button>
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
          </div>
        )}
      </main>
    </div>
  );
}

export default withAuth(UnSubDashboard);