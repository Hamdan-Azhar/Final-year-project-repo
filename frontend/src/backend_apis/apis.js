import Cookies from 'js-cookie';
  //  const API_BASE_URL = "https://modeltrainer-ecci53qs.b4a.run"; // Replace with your base URL
// const API_BASE_URL = "https://d39a-137-59-218-169.ngrok-free.ap"; // Replace with your base URL

// const API_BASE_URL = "http://127.0.0.1:8000";
// const API_BASE_URL = "https://fyp-backend-9sn2.onrender.com";
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;
console.log("API_BASE_URL", API_BASE_URL);

const apiUrls = {
  login: `${API_BASE_URL}/login/`,
  signup: `${API_BASE_URL}/signup/`,
  forget: `${API_BASE_URL}/forget/`,
  payment: `${API_BASE_URL}/payment/`, 
  get_profile: `${API_BASE_URL}/get-user/`,
  update_profile: `${API_BASE_URL}/update-user/`,
  
  get_videos: `${API_BASE_URL}/get-videos/`,

  client_request: `${API_BASE_URL}/client_request/`,
  get_users: `${API_BASE_URL}/get-users/`, 

  otp: `${API_BASE_URL}/otp/`, 
  resend_otp: `${API_BASE_URL}/resend_otp/`, 
  upload_video: `${API_BASE_URL}/upload-video/`, 
  delete_user: `${API_BASE_URL}/delete-user/`, 

  delete_video: `${API_BASE_URL}/delete-video/`,
  get_video: `${API_BASE_URL}/get-video/`,
  update_subscription: `${API_BASE_URL}/update_subscription/`,

  // deletePost: (postId) => `${API_BASE_URL}/posts/${postId}`, // Dynamic URL example
};

export default apiUrls;
