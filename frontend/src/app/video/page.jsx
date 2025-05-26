"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from 'next/navigation';
import Button from "@/components/Button";
import Cookies from 'js-cookie';
import axios from "axios";
import apiUrls from "@/backend_apis/apis";
import Header from "@/components/Header";
import Loader from "@/components/Loader";
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
          headers: { Authorization: `Bearer ${token}` },
        });

        setData(response.data);
      } catch (error) {
        setError(error.response?.data?.error || "Failed to fetch video data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [videoName]);

  return (
    <Suspense fallback={<Loader size={8} />}>
      <div className="min-h-screen bg-white text-gray-900">
        <Header navItems={[{ name: 'Dashboard', url: '/owner_dashboard' }]} />

        <main className="p-8 flex justify-center">
          <div className="w-full max-w-6xl space-y-8">
            <h1 className="text-3xl font-bold text-center">{videoName}</h1>

            <div className="relative w-full h-[500px] bg-gray-900 rounded-lg overflow-hidden flex justify-center items-center">
              {loading ? (
                <Loader size={20} />
              ) : error ? (
                <p className="text-red-500 text-center">{error}</p>
              ) : (
                <video src={data?.url} controls className="w-full h-full" />
              )}
            </div>

            <div className="rounded-md p-6">
              {loading ? (
                <div className="flex justify-center">
                  <Loader size={12} />
                </div>
              ) : error ? (
                <p className="text-red-500 text-center">{error}</p>
              ) : (
                    data.classification && (
                  <a
                    href={data.classification}
                    download
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block mt-4"
                  >
                    <Button className="w-full">Download Classification Report</Button>
                  </a>
                )
                // <h2 className="text-3xl font-bold text-center">
                //   Activity classified by {data.model_type}: {data.classification}
                // </h2>
              )}
            </div>
          </div>
        </main>
      </div>
    </Suspense>
  );
};

export default withAuth(VideoPage);
