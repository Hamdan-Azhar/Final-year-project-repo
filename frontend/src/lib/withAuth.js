// "use client";

// import { useEffect, useState } from "react";
// import { useRouter } from "next/navigation";
// import Cookies from "js-cookie";
// import Loader from "@/components/Loader";

// const withAuth = (WrappedComponent) => {
//   return (props) => {
//     const router = useRouter();
//     const [isLoading, setIsLoading] = useState(true); // Track loading state

//     useEffect(() => {
//       const token = Cookies.get("access_token");
//       const userRole = Cookies.get("user_role");
//       const subscription = Cookies.get("subscription");

//       if (!token) {
//         router.push("/login");
//         // setIsLoading(false);
//         return;
//       }

//       if (userRole === "admin") {
//         router.push("/admin_member");
//         // setIsLoading(false);
//         return;
//       }

//       if (subscription !== "True") {
//         router.push("/unsubdashboard");
//         setIsLoading(false);
//         return;
//       }

//       setIsLoading(false); // Only set loading to false if no redirection occurs
//     }, [router]);

//     if (isLoading) {
//       return (<div className="flex justify-center items-center min-h-screen w-full">
//             <Loader size={12}/>
//             </div>);
//     }

//     return <WrappedComponent {...props} />;
//   };
// };

// export default withAuth;


"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Cookies from "js-cookie";
import Loader from "@/components/Loader";
import parseJWT from "./parseJWT";


// otp, subdashboard, unsubdashboard, edit_profile, admin, video
function withAuth(WrappedComponent) {
  return (props) => {
    const router = useRouter();
    const pathname = usePathname(); // Get current route
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
      const storedEmail = localStorage.getItem('signup_email');
      const storedExpiry = localStorage.getItem('otp_expires_at');
      console.log(storedEmail, storedExpiry);
      

      if (pathname === "/otp") {
        console.log("inside otp");
        if (!storedEmail && !storedExpiry) {
        router.push('/login');
        return;
        } else {
          setIsLoading(false);
          return;
        }
      }

      let token = Cookies.get("access_token");
      token = token ? parseJWT(token) : null;
    
      if (!token) {
        console.log("not logged in");
        router.push("/login");
        return;
      } else if (token.is_admin && !["/admin", "/edit_profile"].includes(pathname)) {
        router.push("/admin");
        return;
      } else if (token.is_subscribed && !["/subdashboard", "/video", "/edit_profile"].includes(pathname)) {
        console.log("subscribed");
        router.push("/subdashboard");
        return;
      } else if (!token.is_subscribed && !token.is_admin && !["/unsubdashboard", "/edit_profile"].includes(pathname)) {
        router.push("/unsubdashboard");
        return;
      }
      // }

      // if (!token && pathname !== "/login") {
      //   console.log("not logged in");
      //   router.push("/login");
      //   return;
      // }

      // if (token['is_admin'] && pathname !== "/admin_member") {
      //   console.log("admin");
      //   router.push("/admin_member");
      //   return;
      // }

      // if (!token['is_admin'] && !token['is_subscribed'] && pathname !== "/unsubdashboard") {
      //   console.log("not subscribed");
      //   router.push("/unsubdashboard");
      //   return;
      // }

      setIsLoading(false);
    }, [router, pathname]);

    if (isLoading) {
      return (
        <div className="flex justify-center items-center min-h-screen w-full">
          <Loader size={14} />
        </div>
      );
    }

    return <WrappedComponent {...props} />;
  };
};

export default withAuth;
