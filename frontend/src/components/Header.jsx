import React from 'react';
import Link from 'next/link';

const Header = ({ navItems = [], buttons = [], userInfo }) => {
  return (
    <header className="w-full flex justify-between items-center py-4 px-6 md:px-16 border-b border-gray-200 bg-white">
      <Link href="/">
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">ExamGuard</h1>
      </Link>

      <nav className="flex items-center space-x-6">
        {/* Navigation Links */}
        {navItems.map((item, index) => (
          <Link key={index} href={item.url}>
            <span className="relative text-base font-medium text-gray-700 cursor-pointer group">
              {item.name}
              <span className="absolute left-0 bottom-[-8px] w-0 h-1 bg-purple-600 transition-all duration-300 group-hover:w-full rounded-full"></span>
            </span>
          </Link>
        ))}

        {/* User Info */}
        {userInfo && (
          <div className="text-base text-gray-700 font-medium bg-gray-100 px-3 py-1 rounded-full">
            {userInfo.name} • {userInfo.role}
          </div>
        )}

        {/* Buttons */}
        {buttons.map((button, index) => (
          <Link
            key={index}
            href={button.url}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700 transition"
            onClick={button.onClick}
          >
            {button.name}
          </Link>
        ))}
      </nav>
    </header>
  );
};

export default Header;


