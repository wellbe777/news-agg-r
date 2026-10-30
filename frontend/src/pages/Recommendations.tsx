import { useQuery } from "@tanstack/react-query";
import api from "../lib/api";

export default function Recommendations() {
  const { data, isLoading } = useQuery({
    queryKey: ["recommendations"],
    queryFn: async () => {
      const res = await api.get("/recommendations/");
      return res.data;
    },
  });

  if (isLoading) return <p>Loading...</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Your Recommendations</h2>
      <ul className="space-y-2">
        {data?.results?.map((article: any) => (
          <li key={article.id} className="p-4 bg-white shadow rounded">
            <h3 className="font-semibold">{article.title}</h3>
            <p className="text-sm text-gray-600">{article.source?.name}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
