"use client";

import React, { useState, useEffect } from "react";
import apiUrls from "../../backend_apis/apis";
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import withAuth from "@/lib/withAuth";
import Header from "@/components/Header";
import Button from "@/components/Button";
import axios from "axios";

const SubDashboard = () => {
  const [storage, setStorage] = useState({ used: "0.00 GB", remaining: "10.00 GB", total: "10 GB" });
  const [videos, setVideos] = useState([]);
  const [selectedModel, setSelectedModel] = useState("Deep Learning Model");
  const token = Cookies.get('access_token');
  const router = useRouter();
  const [videoFile, setVideoFile] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [classificationResult, setClassificationResult] = useState(null); // Result state


  const fetchData = async () => {
    try {
      const response = await axios.get(apiUrls.get_videos, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
  
      const data = response.data;
      setStorage(data.cloud_storage);
      setVideos(data.videos);
    } catch (error) {
      console.error("Error fetching data:", error);
  
      if (error.response) {
        console.log(error.response.data.error);
      }
    }
  };

  useEffect(() => {
    fetchData();
  }, []);


  const handleDeleteVideo = async (name) => {
    try {
      await axios.delete(`${apiUrls.delete_video}${name}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      // setIsLoading(true);
      setVideos(videos.filter(video => video.name !== name));
    } catch (error) {
      console.error("Error deleting video:", error);
      if (error.response) {
        // Handle specific error statuses
        console.log(error.response.data.error);
      }
    }
  };

  const handleClickVideo = (assetId) => {
    router.push(`/video?videoName=${assetId}`);
  };

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
      formData.append('model_type', selectedModel);

      try {
        const response = await axios.post(apiUrls.upload_video, formData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log(response.data.message);
        setClassificationResult(response.data.classification);
        fetchData();
      } catch (error) {
        console.error('Error uploading video:', error);
      }
    };
   
  const handleDeleteVideoPreview = () => {
      setVideoFile(null);
      setVideoPreview(null);
      setClassificationResult(null); // Clear result when deleting video
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center">
      {/* Header  p-6*/}
      <Header navItems={[{ name: 'Pricing', url: '/Pricing' }, { name: 'Profile', url: '/edit_profile' }]} buttons={[{ name: 'Logout', url: '/login' , onClick: () => Cookies.remove('access_token')}]}/>

      {/* Main Content */}
      <main className="w-full max-w-4xl mt-8 p-6">
        {/* Title */}
        <h2 className="text-3xl font-bold mb-6">Dashboard</h2>

        {/* Selected AI Model */}
        <div className="mb-8">
          <label className="text-lg font-medium block mb-2">Selected AI Model</label>
          <select
            className="w-full bg-[#26303B] text-white p-3 rounded-md border border-gray-700"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option>Deep Learning Model</option>
            <option>Machine Learning Model</option>
          </select>
        </div>

        {/* Cloud Storage */}
        <div className="mb-8">
          <label className="text-lg font-medium block mb-2">Cloud Storage</label>
          <div className="p-4 rounded-lg">
            <div className="text-sm mb-2">{storage.used} used</div>
            <div className="w-full bg-[#26303B] rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${(parseFloat(storage.used) / parseFloat(storage.total)) * 100}%` }}
              ></div>
            </div>
            <div className="text-sm mt-2">{storage.remaining} remaining</div>
          </div>
        </div>

        {/* Video Uploads */}
        <div>
          <label className="text-lg font-medium block mb-4">Video uploads</label>
          <div className="p-1 rounded-lg border border-gray-700">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b border-gray-700">Video name</th>
                  <th className="py-2 px-4 border-b border-gray-700">Storage</th>
                  <th className="py-2 px-4 border-b border-gray-700">Action</th>
                </tr>
              </thead>
              <tbody>
                {videos.map((video, index) => (
                  <tr key={index}>
                    <td className="py-2 px-4 cursor-pointer" onClick={() => handleClickVideo(video.name)}>{video.name}</td>
                    <td className="py-2 px-4 cursor-pointer">{video.size}</td>
                    <td className="py-2 px-4 cursor-pointer">
                      <Button
                        onClick={() => handleDeleteVideo(video.name)}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="flex flex-col items-center justify-center">
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
                    onClick={handleDeleteVideoPreview}
                    className="w-full"
                  >
                  Delete Video
                  </Button>
                </div>

                {/* Classification Result*/}
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
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default withAuth(SubDashboard);