
"use client";
// import '@fontsource/inter/variable.css';
import { use, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import apiUrls from "../../backend_apis/apis";
import Header from "@/components/Header";
import Button from "@/components/Button";
import Cookies from "js-cookie";
import { useEffect } from "react";
import withAuth from "@/lib/withAuth";


const EditProfilePage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmpassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false); 
  const token = Cookies.get("access_token");
  const router = useRouter();

  useEffect(() => {
    const fetchProfile = async () => {
      console.log("wirk");
      try {
        const response = await axios.get(apiUrls.get_profile, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        console.log(response.status, "----response.ok-------------", response.data);
        setUsername(response.data.name);
        setPassword(response.data.password);
        setConfirmPassword(response.data.password);
      } catch (error) {
        if (error.response){
          setError(error.response.data.error);
        }
      }     
    }

    fetchProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
  
  
    // const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$/;
    // if (!passwordRegex.test(password)) {
    //   setError("Password must be at least 8 characters long...");
    //   setIsLoading(false);
    //   return;
    // }
  
    if (password !== confirmpassword) {
      setError("Password and Confirm Password do not match.😊");
      setIsLoading(false);
      return;
    }
  
    setError("");
  
    const payload = {
      name: username,
      password: password,
    };
  
    try {
      const response = await axios.put(apiUrls.update_profile, payload, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      console.log(response.status, "----response.ok-------------", response.data);
      // Redirect to login
      router.push('/login');
    } catch (error) {
      if (error.response){
        const data = error.response.data;
        setError(data.error);
      } else {
      setError("An error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <Header navItems={[{ name: 'Dashboard', url: '/subdashboard' }, { name: 'Pricing', url: '/Pricing' }]}
              buttons={[{ name: 'Logout', url: '/login', onClick: () => Cookies.remove('access_token') }]}/>

      {/* Main Form */}
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="w-full max-w-md">
          <h2 className="text-2xl  text-center mb-6 font-inter">
            Edit your profile
          </h2>

          {/* Error Message */}
          {error && (
            <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <input
                type="text"
                id="username"
                onChange={(e) => setUsername(e.target.value)}
                value={username}
                placeholder="Enter your username"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mb-4">
              <input
                type="password"
                id="password"
                onChange={(e) => setPassword(e.target.value)}
                value={password}
                placeholder="Enter your password"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mb-4">
              <input
                type="password"
                id="confirm-password"
                onChange={(e) => setConfirmPassword(e.target.value)}
                value={confirmpassword}
                placeholder="Confirm password"
                className="block w-full px-4 py-3 border border-gray-600 rounded-xl bg-gray-800 text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <Button
              type="submit"
              loading={isLoading}
              className="w-full"
            >
              Save changes
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default withAuth(EditProfilePage);