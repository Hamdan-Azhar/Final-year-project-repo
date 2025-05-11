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