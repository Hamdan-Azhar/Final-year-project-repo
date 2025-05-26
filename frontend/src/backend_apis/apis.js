
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;

const apiUrls = {
  login: `${API_BASE_URL}/login/`,
  signup: `${API_BASE_URL}/signup/`,
  get_user: `${API_BASE_URL}/get-user/`,
  update_user: `${API_BASE_URL}/update-user/`,
  get_videos: `${API_BASE_URL}/get-videos/`,
  get_all_videos: `${API_BASE_URL}/get-all-videos/`,
  get_users: `${API_BASE_URL}/get-users/`,
  otp: `${API_BASE_URL}/otp/`,
  resend_otp: `${API_BASE_URL}/resend_otp/`,
  upload_video: `${API_BASE_URL}/upload-video/`,
  delete_user: `${API_BASE_URL}/delete-user/`,
  delete_video: `${API_BASE_URL}/delete-video/`,
  get_video: `${API_BASE_URL}/get-video/`,
  update_subscription: `${API_BASE_URL}/update_subscription/`,
  check_subscription: `${API_BASE_URL}/check-subscription/`,
  request_subscription: `${API_BASE_URL}/request-subscription/`,
  get_all_requests: `${API_BASE_URL}/get-all-requests/`,
  get_faculty_members: `${API_BASE_URL}/get-faculty-members/`,
  create_faculty_member: `${API_BASE_URL}/create-faculty-member/`,
  delete_faculty_member: `${API_BASE_URL}/delete-faculty-member/`,
  create_faculty_member_subject: `${API_BASE_URL}/create-faculty-member-subject/`,
  delete_faculty_member_subject: `${API_BASE_URL}/delete-faculty-member-subject/`,
  get_faculty_member: `${API_BASE_URL}/get-faculty-member/`
};

export default apiUrls;
