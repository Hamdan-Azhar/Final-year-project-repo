
// "use client";

// import { useEffect, useState } from "react";
// import { useRouter, usePathname } from "next/navigation";
// import Cookies from "js-cookie";
// import Loader from "@/components/Loader";
// import parseJWT from "./parseJWT";


// // otp, subdashboard, unsubdashboard, edit_profile, admin, video
// function withAuth(WrappedComponent) {
//   return (props) => {
//     const router = useRouter();
//     const pathname = usePathname(); // Get current route
//     const [isLoading, setIsLoading] = useState(true);

//     useEffect(() => {
//       const storedEmail = localStorage.getItem('signup_email');
//       const storedExpiry = localStorage.getItem('otp_expires_at');
//       console.log(storedEmail, storedExpiry);
      

//       if (pathname === "/otp") {
//         console.log("inside otp");
//         if (!storedEmail && !storedExpiry) {
//         router.push('/login');
//         return;
//         } else {
//           setIsLoading(false);
//           return;
//         }
//       }

//       let token = Cookies.get("access_token");
//       token = token ? parseJWT(token) : null;
    
//       if (!token) {
//         console.log("not logged in");
//         router.push("/login");
//         return;
//       } else if (token.is_admin && !["/admin", "/edit_profile"].includes(pathname)) {
//         router.push("/admin");
//         return;
//       } else if (token.is_subscribed && !["/subdashboard", "/video", "/edit_profile"].includes(pathname)) {
//         console.log("subscribed");
//         router.push("/subdashboard");
//         return;
//       } else if (!token.is_subscribed && !token.is_admin && !["/unsubdashboard", "/edit_profile"].includes(pathname)) {
//         router.push("/unsubdashboard");
//         return;
//       }
//       // }

//       // if (!token && pathname !== "/login") {
//       //   console.log("not logged in");
//       //   router.push("/login");
//       //   return;
//       // }

//       // if (token['is_admin'] && pathname !== "/admin_member") {
//       //   console.log("admin");
//       //   router.push("/admin_member");
//       //   return;
//       // }

//       // if (!token['is_admin'] && !token['is_subscribed'] && pathname !== "/unsubdashboard") {
//       //   console.log("not subscribed");
//       //   router.push("/unsubdashboard");
//       //   return;
//       // }

//       setIsLoading(false);
//     }, [router, pathname]);

//     if (isLoading) {
//       return (
//         <div className="flex justify-center items-center min-h-screen w-full">
//           <Loader size={14} />
//         </div>
//       );
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

function withAuth(WrappedComponent) {
  const AuthWrapper = (props) => {
    const router = useRouter();
    const pathname = usePathname();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
      const verifyAuth = () => {
        const storedEmail = localStorage.getItem('signup_email');
        const storedExpiry = localStorage.getItem('otp_expires_at');

        if (pathname === "/otp") {
          if (!storedEmail && !storedExpiry) {
            router.push('/login');
            return;
          }
          setIsLoading(false);
          return;
        }

        const token = Cookies.get("access_token");
        const parsedToken = token ? parseJWT(token) : null;
      
        if (!parsedToken) {
          router.push("/login");
          return;
        }

        if (parsedToken.is_admin && !["/admin", "/edit_profile"].includes(pathname)) {
          router.push("/admin");
          return;
        }

        if (parsedToken.is_subscribed && !["/subdashboard", "/video", "/edit_profile"].includes(pathname)) {
          router.push("/subdashboard");
          return;
        }

        if (!parsedToken.is_subscribed && !parsedToken.is_admin && !["/unsubdashboard", "/edit_profile"].includes(pathname)) {
          router.push("/unsubdashboard");
          return;
        }

        setIsLoading(false);
      };

      verifyAuth();
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

  // Add displayName to fix the ESLint error
  AuthWrapper.displayName = `WithAuth(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;
  return AuthWrapper;
}

export default withAuth;