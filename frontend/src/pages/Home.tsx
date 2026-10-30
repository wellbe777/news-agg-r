import { useEffect, useState } from "react";
import API from "../api/api";
import Card from "../components/Card";

interface Article {
  id: number;
  title: string;
  summary: string;
  published_at: string;
  source: { name: string };
}

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const res = await API.get("articles/?limit=5"); // cursor pagination
        setArticles(res.data.results || res.data); // depending on pagination
      } catch (err) {
        console.error("Error fetching articles", err);
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 py-6">
      <Card title="Latest News">
        {loading ? (
          <p>Loading...</p>
        ) : (
          <ul className="space-y-3">
            {articles.map((article) => (
              <li key={article.id} className="border-b pb-2">
                <h3 className="font-medium">{article.title}</h3>
                <p className="text-sm text-gray-600">{article.source?.name} • {new Date(article.published_at).toLocaleDateString()}</p>
                <p className="text-gray-700 text-sm">{article.summary}</p>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card title="Your Interests">
        <p>Select categories like <strong>Tech</strong>, <strong>Sports</strong>, or <strong>Politics</strong> to personalize your feed.</p>
      </Card>
    </div>
  );
}

