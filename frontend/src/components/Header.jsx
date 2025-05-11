// src/components/Header.jsx
import React from 'react';
import Link from 'next/link';

const Header = ({ navItems = [], buttons = []}) => {
  return (
    <header className="w-full flex justify-between items-top py-4 px-6 border-b border-gray-700">
      <Link href="/">
        <h1 className="text-2xl font-bold">ExamGuard</h1>
      </Link>
      <nav className="flex items-center justify-end space-x-6 text-gray-300 text-xs">
        {/* Render navigation links */}
        {navItems.map((item, index) => (
          <Link key={index} href={item.url} className="text-lg font-medium hover:text-blue-500">
            {item.name}
          </Link>
        ))}

        {/* Render buttons */}
        {buttons.map((button, index) => (
          <Link
            key={index}
            href={button.url}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg text-lg font-medium hover:bg-blue-600 transition-colors"
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




// // src/components/Header.jsx
// import React from 'react';
// import Link from 'next/link';
// import Button from './Button';

// const Header = ({ navItems = [], buttons = [] }) => {
//   // Function to add delay to button clicks
//   const handleClickWithDelay = async (originalOnClick) => {
//     if (originalOnClick) {
//       // Add 2 second delay before executing the original onClick
//       await new Promise(resolve => setTimeout(resolve, 2000));
//       await originalOnClick();
//     }
//   };

//   return (
//     <header className="w-full flex justify-between items-top py-4 px-6 border-b border-gray-700">
//       <Link href="/">
//         <h1 className="text-2xl font-bold cursor-pointer">ExamGuard</h1>
//       </Link>
//       <nav className="flex items-center justify-end space-x-6 text-gray-300 text-xs">
//         {/* Render navigation links */}
//         {navItems.map((item, index) => (
//           <Link key={index} href={item.url} className="text-lg font-medium hover:text-blue-500">
//             {item.name}
//           </Link>
//         ))}

//         {/* Render buttons with delay */}
//         {buttons.map((button, index) => (
//           <Link key={index} href={button.url} passHref legacyBehavior>
//             <Button
//               className="px-4 py-2 rounded-lg text-lg font-medium hover:bg-blue-600 transition-colors"
//               onClick={() => handleClickWithDelay(button.onClick)}
//             >
//               {button.name}
//             </Button>
//           </Link>
//         ))}
//       </nav>
//     </header>
//   );
// };

// export default Header;