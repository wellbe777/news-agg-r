// src/pages/RecommendationPage.tsx

import React from "react";
import { useAuth } from "../context/AuthContext";
import useRecommendationFeed from "../hooks/useRecommendationFeed";
import ArticleList from "../components/ArticleList";

export default function RecommendationPage() {
    const { user } = useAuth();
    const { articles, loadMore, next, loading } = useRecommendationFeed();

    if (!user) {
        return (
            <div className="text-center mt-16 text-gray-600">
                <h2 className="text-xl font-semibold">Recommendations</h2>
                <p className="mt-3">You must log in to see your recommendations.</p>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto p-6">
            <h1 className="text-2xl font-bold mb-6">Your Recommendations</h1>

            <ArticleList articles={articles} />

            {next && (
                <div className="text-center mt-6">
                    <button
                        onClick={loadMore}
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                        {loading ? "Loading..." : "Load More"}
                    </button>
                </div>
            )}
        </div>
    );
}
