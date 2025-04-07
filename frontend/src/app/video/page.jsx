"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from 'next/navigation';
import Cookies from 'js-cookie';
import Header from "@/components/Header";
import Loader from "@/components/Loader"; // Import the Loader component
import apiUrls from "@/backend_apis/apis";
import axios from "axios";
import withAuth from "@/lib/withAuth";

const VideoPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const searchParams = useSearchParams();
  const videoName = searchParams.get('videoName');
  const token = Cookies.get('access_token');

  useEffect(() => {
    if (!videoName) return;
    
    const fetchData = async () => {
    try {
      const response = await axios.get(`${apiUrls.get_video}${videoName}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setData(response.data);
      setLoading(false);
    } catch (error) {
      if (error.response) {
        // Handle specific HTTP error statuses
        setError(error.response.data.error);
      } else {
        // Handle network errors or other issues
        setError("Failed to fetch data");
      }
      setLoading(false);
    }
  };

  fetchData();
  }, [videoName]);

  useEffect(() => {
    if (data) {
      console.log("Video data loaded:", data.url);
    }
  }, [data]);

  return (
    <Suspense fallback={<Loader size={8} />}>
      <div className="min-h-screen bg-black text-white">
        <Header navItems={[{ name: 'Dashboard', url: '/subdashboard' }]}/>
        
        <main className="p-8 flex justify-center">
          <div className="w-full max-w-6xl space-y-8">
            {/* Video Title */}
            <h1 className="text-3xl font-bold text-center">
              {videoName}
            </h1>
            
            {/* Video Section */}
            <div className="relative w-full h-[500px] bg-gray-900 rounded-lg overflow-hidden flex justify-center items-center">
              {loading ? (
                <Loader size={20} /> /* Large loader for video */
              ) : error ? (
                <p className="text-center text-red-500">{error}</p>
              ) : (
                <video
                  src={data?.url}
                  controls
                  className="w-full h-full"
                >
                  Your browser does not support the video tag.
                </video>
              )}
            </div>

            {/* Data Section */}
            <div className="rounded-md p-6">
              {loading ? (
                <div className="flex justify-center">
                  <Loader size={12} /> {/* Medium loader for data */}
                </div>
              ) : error ? (
                <p className="text-center text-red-500">{error}</p>
              ) : (
                <div className="overflow-x-auto">
                  <h2 className="text-3xl font-bold text-center">
                  Activity classified by {data.model_type}: {data.classification}
                  </h2>
                  {/* <table className="w-full border text-sm border-collapse table-fixed">
                    <thead>
                      <tr className="border-b bg-black text-white-400">
                        <th className="p-4 text-center">Person</th>
                        <th className="p-4 text-center">Activity Detected</th>
                      </tr>
                    </thead> 
                    <tbody>
                      {Array.isArray(data?.classes) ? (
                        data.classes
                          .filter(item => typeof item === 'string' && item.trim() !== "")
                          .map((item, index) => (
                            <tr key={index} className="border-b border-gray-700">
                              <td className="p-4">{index + 1}</td>
                              <td className="p-4">{item.trim()}</td>
                            </tr>
                          ))
                      ) : (
                        <tr>
                          <td colSpan="2" className="p-4 text-center">
                            No data available
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table> */}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </Suspense>
  );
}

export default withAuth(VideoPage);