// src/hooks/useRecommendationFeed.ts

import { useState, useCallback } from "react";
import api from "../api/api";
import type { Article, PaginatedResponse } from "../types/Article";

export default function useRecommendationFeed() {
    const [articles, setArticles] = useState<Article[]>([]);
    const [next, setNext] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const load = useCallback(async (url?: string) => {
        if (loading) return;

        setLoading(true);

        try {
            const endpoint = url || "/recommendations/";
            const res = await api.get<PaginatedResponse<Article>>(endpoint);

            setArticles(prev =>
                url ? [...prev, ...res.data.results] : res.data.results
            );

            setNext(res.data.next);
        } catch (e) {
            console.error("Recommendation fetch error:", e);
        } finally {
            setLoading(false);
        }
    }, [loading]);

    const loadMore = useCallback(() => {
        if (next) load(next);
    }, [next, load]);

    // initial load
    if (articles.length === 0 && !loading) {
        load();
    }

    return { articles, next, loadMore, loading };
}
