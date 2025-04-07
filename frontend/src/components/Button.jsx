"use client";
import { useState } from "react";
import Loader from "./Loader";

const Button = ({
  onClick,
  children,
  className = "",
  disabled = false,
  loading = false,
  type = "button",
  ...props
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async (e) => {
    if (onClick) {
      setIsLoading(true);
      try {
        await onClick(e);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const showLoading = loading || isLoading;

  return (
    <button
      type={type}
      onClick={handleClick}
      disabled={disabled || showLoading}
      className={`
        relative bg-blue-600 text-white py-2 px-4 rounded-xl 
        hover:bg-blue-700 transition flex items-center justify-center
        ${showLoading ? "opacity-90 cursor-not-allowed" : ""}
        ${className}
      `}
      {...props}
    >
      {showLoading ? (
        <Loader size={5}/>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;