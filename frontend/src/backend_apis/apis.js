
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;

const apiUrls = {
  login: `${API_BASE_URL}/login/`,
  signup: `${API_BASE_URL}/signup/`,
  get_profile: `${API_BASE_URL}/get-user/`,
  update_profile: `${API_BASE_URL}/update-user/`,
  get_videos: `${API_BASE_URL}/get-videos/`,
  get_users: `${API_BASE_URL}/get-users/`,
  otp: `${API_BASE_URL}/otp/`,
  resend_otp: `${API_BASE_URL}/resend_otp/`,
  upload_video: `${API_BASE_URL}/upload-video/`,
  delete_user: `${API_BASE_URL}/delete-user/`,
  delete_video: `${API_BASE_URL}/delete-video/`,
  get_video: `${API_BASE_URL}/get-video/`,
  update_subscription: `${API_BASE_URL}/update_subscription/`,
};

export default apiUrls;
