import React from "react";
//import type { ReactNode } from "react";
//import Navbar from "./Navbar";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <main className="flex-grow container mx-auto px-4 py-8 max-w-5xl">
        {children}
      </main>
      <footer className="py-4 text-center text-sm text-gray-500 border-t">
        © {new Date().getFullYear()} News Aggregator
      </footer>
    </div>
  );
};

export default Layout;
