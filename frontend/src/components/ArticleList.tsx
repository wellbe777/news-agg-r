// src/components/ArticleList.tsx

import React from "react";
import type { Article } from "../types/Article";

interface Props {
    articles: Article[];
}

export default function ArticleList({ articles }: Props) {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map(article => (
                <div
                    key={article.id}
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden hover:shadow-lg transition"
                >
                    {article.image_url && (
                        <img
                            src={article.image_url}
                            alt={article.title}
                            className="h-48 w-full object-cover"
                        />
                    )}

                    <div className="p-4 flex flex-col">
                        <h2 className="text-lg font-semibold line-clamp-2 mb-2 dark:text-white">
                            <a
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:text-blue-600 dark:hover:text-blue-400"
                            >
                                {article.title}
                            </a>
                        </h2>

                        <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3 flex-grow">
                            {article.summary || article.content}
                        </p>

                        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-3">
                            <span>
                                {typeof article.source === "string"
                                    ? article.source
                                    : article.source?.name}
                            </span>
                            <span>{new Date(article.published_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
