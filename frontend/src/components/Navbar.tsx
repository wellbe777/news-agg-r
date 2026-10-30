import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="w-screen bg-gray-900 text-white px-6 py-4 flex items-center justify-between shadow-md">
      <div className="text-xl font-semibold">
        <Link to="/" className="hover:text-gray-300">
          📰 NewsAgg
        </Link>
      </div>

      <div className="space-x-6 flex items-center">
        {user ? (
          <>
            <Link
              to="/feed"
              className="hover:text-gray-300 transition-colors duration-200"
            >
              Feed
            </Link>
            <Link
              to="/interests"
              className="hover:text-gray-300 transition-colors duration-200"
            >
              Interests
            </Link>
            <Link to="/recommendations" className="px-4 py-2">
              Recommendations
            </Link>
            <Link
              to="/profile"
              className="hover:text-gray-300 transition-colors duration-200"
            >
              Profile
            </Link>
            <button
              onClick={logout}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-md text-sm font-medium transition"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              to="/login"
              className="hover:text-gray-300 transition-colors duration-200"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="hover:text-gray-300 transition-colors duration-200"
            >
              Register
            </Link>
          </>
        )}
        {/* 🌙 Dark/Light toggle */}
          <button
            onClick={toggleTheme}
            className="px-2 py-1 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100 transition-colors duration-300"
            title="Toggle theme"
          >
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
      </div>
    </nav>
  );
};

export default Navbar;
