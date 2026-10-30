// frontend/src/pages/Feed.tsx
import React, { useState, useEffect, useCallback } from "react";
import api from "../api/api";
import { useAuth } from "../context/AuthContext";

interface Category {
  id: number;
  name: string;
}

interface Source {
  id?: number;
  name: string;
  homepage?: string;
}

interface Article {
  id: number;
  title: string;
  summary?: string;
  content?: string;
  url: string;
  image_url?: string;
  published_at: string;
  source?: Source | string;
  categories: (Category | string)[];
}

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Article[];
}

const Feed: React.FC = () => {
  // ------------------------------------------------
  // State
  // ------------------------------------------------
  const [articles, setArticles] = useState<Article[]>([]);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const [categories, setCategories] = useState<Category[]>([]);
  const [sources, setSources] = useState<Source[]>([]);

  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedSource, setSelectedSource] = useState("");

  const { user } = useAuth();
  const isLoggedIn = !!user;

  // NEW: feed mode toggle
  const [feedMode, setFeedMode] = useState<"interests" | "all">("interests");

  useEffect(() => {
  if (!isLoggedIn) {
    setFeedMode("all");        // always show all articles
  }
  }, [isLoggedIn]);

  // ------------------------------------------------
  // Debounce search input
  // ------------------------------------------------
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // ------------------------------------------------
  // Load categories & sources
  // ------------------------------------------------
  useEffect(() => {
    async function fetchFilters() {
      try {
        const [catRes, srcRes] = await Promise.all([
          api.get("/categories/"),
          api.get("/sources/"),
        ]);
        setCategories(catRes.data);
        setSources(srcRes.data);
      } catch (err) {
        console.error("Error loading filters:", err);
      }
    }
    fetchFilters();
  }, []);

  // ------------------------------------------------
  // Reset filters & search
  // ------------------------------------------------
  const resetFilters = useCallback(() => {
    setSearchTerm("");
    setDebouncedSearch("");
    setSelectedCategory("");
    setSelectedSource("");
  }, []);

  // ------------------------------------------------
  // Main fetch function
  // ------------------------------------------------
  const fetchArticles = useCallback(
    async (url?: string) => {
      setLoading(true);

      try {
        const params = new URLSearchParams({
          use_interests: feedMode === "interests" ? "true" : "false",
        });

        if (debouncedSearch) params.append("search", debouncedSearch);
        if (selectedCategory) params.append("category", selectedCategory);
        if (selectedSource) params.append("source", selectedSource);

        const endpoint = url || `/articles/?${params.toString()}`;
        const res = await api.get<PaginatedResponse>(endpoint);

        setArticles((prev) =>
          url ? [...prev, ...res.data.results] : res.data.results
        );

        setNextPage(res.data.next);
      } catch (err) {
        console.error("Error fetching articles:", err);
      } finally {
        setLoading(false);
      }
    },
    [debouncedSearch, selectedCategory, selectedSource, feedMode]
  );

  // ------------------------------------------------
  // Reload articles when filters/search/mode changes
  // ------------------------------------------------
  useEffect(() => {
    fetchArticles();
  }, [debouncedSearch, selectedCategory, selectedSource, feedMode, fetchArticles]);

  // ------------------------------------------------
  // Load more handler
  // ------------------------------------------------
  const handleLoadMore = () => {
    if (nextPage) {
      fetchArticles(nextPage);
    }
  };

  // ------------------------------------------------
  // Switch feed mode
  // ------------------------------------------------
  const activateInterestsFeed = () => {
    resetFilters();
    setFeedMode("interests");
  };

  const activateAllArticlesFeed = () => {
    resetFilters();
    setFeedMode("all");  
  };

  // ------------------------------------------------
  // Render
  // ------------------------------------------------
  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* MODE SWITCH */}
      {isLoggedIn && (
        <div className="flex gap-4 mb-6">
          <button
            onClick={activateInterestsFeed}
            className={`px-4 py-2 rounded ${
              feedMode === "interests"
                ? "bg-blue-600 text-white"
                : "bg-gray-200 dark:bg-gray-700 dark:text-white"
            }`}
          >
            My Interests Feed
          </button>

          <button
            onClick={activateAllArticlesFeed}
            className={`px-4 py-2 rounded ${
              feedMode === "all"
                ? "bg-blue-600 text-white"
                : "bg-gray-200 dark:bg-gray-700 dark:text-white"
            }`}
          >
            All Articles
          </button>
        </div>
      )}
      

      {/* SEARCH + FILTERS */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <input
          type="text"
          placeholder="Search articles..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="border rounded-lg p-2 w-full sm:w-1/3"
        />

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="border rounded-lg p-2 w-full sm:w-1/4"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.name}>
              {cat.name}
            </option>
          ))}
        </select>

        <select
          value={selectedSource}
          onChange={(e) => setSelectedSource(e.target.value)}
          className="border rounded-lg p-2 w-full sm:w-1/4"
        >
          <option value="">All Sources</option>
          {sources.map((src) => (
            <option key={src.id} value={src.name}>
              {src.name}
            </option>
          ))}
        </select>
      </div>

      {/* ARTICLE LIST */}
      {articles.length === 0 && !loading ? (
        <p className="text-center text-gray-500">No articles found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article) => (
            <div
              key={article.id}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden flex flex-col hover:shadow-lg transition-shadow duration-300"
            >
              {article.image_url && (
                <img
                  src={article.image_url}
                  alt={article.title}
                  className="w-full h-48 object-cover"
                />
              )}

              <div className="p-4 flex flex-col flex-grow">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    {article.title}
                  </a>
                </h2>

                <p className="text-gray-700 dark:text-gray-300 text-sm flex-grow line-clamp-3">
                  {article.summary || article.content || ""}
                </p>

                <div className="mt-3 text-xs text-gray-500 dark:text-gray-400 flex justify-between items-center">
                  <span>
                    {typeof article.source === "string"
                      ? article.source
                      : article.source?.name}
                  </span>
                  <span>
                    {new Date(article.published_at).toLocaleDateString()}
                  </span>
                </div>

                <div className="mt-3 flex flex-wrap gap-1">
                  {article.categories.map((cat) =>
                    typeof cat === "string" ? (
                      <span
                        key={cat}
                        className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded text-xs"
                      >
                        {cat}
                      </span>
                    ) : (
                      <span
                        key={cat.id}
                        className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded text-xs"
                      >
                        {cat.name}
                      </span>
                    )
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* LOAD MORE */}
      {nextPage && (
        <div className="text-center mt-6">
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Loading..." : "Load More"}
          </button>
        </div>
      )}
    </div>
  );
};

export default Feed;
