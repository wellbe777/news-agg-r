// import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  children: React.ReactNode;
}

export default function Card({ title, children }: CardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-6">
      {title && <h2 className="text-lg font-semibold mb-4">{title}</h2>}
      <div className="text-gray-700">{children}</div>
    </div>
  );
}
