import React, { useEffect, useState } from "react";
import api from "../api/api";

interface Category {
  id: number;
  name: string;
}

interface Source {
  id: number;
  name: string;
}

const Interests: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [sources, setSources] = useState<Source[]>([]);

  // 🔹 What user is selecting right now
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [selectedSources, setSelectedSources] = useState<number[]>([]);

  // 🔹 What is actually saved in the backend
  const [savedCategories, setSavedCategories] = useState<Category[]>([]);
  const [savedSources, setSavedSources] = useState<Source[]>([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // Load available & saved interests
  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const [catRes, srcRes, userRes] = await Promise.all([
          api.get("/categories/"),
          api.get("/sources/"),
          api.get("/user/interests/"),
        ]);

        if (!mounted) return;

        setCategories(catRes.data);
        setSources(srcRes.data);

        // Saved from backend
        const user = userRes.data;
        setSelectedCategories(user.category_ids ?? []);
        setSelectedSources(user.source_ids ?? []);

        setSavedCategories(user.categories ?? []);
        setSavedSources(user.sources ?? []);
      } catch (err) {
        console.error("Failed to load interests:", err);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();
    return () => { mounted = false };
  }, []);

  // Toggle handlers
  const toggleCategory = (id: number) =>
    setSelectedCategories((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );

  const toggleSource = (id: number) =>
    setSelectedSources((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );

  // Select All / Clear All
  const selectAllCategories = () =>
    setSelectedCategories(categories.map((c) => c.id));

  const clearAllCategories = () => setSelectedCategories([]);

  const selectAllSources = () => setSelectedSources(sources.map((s) => s.id));

  const clearAllSources = () => setSelectedSources([]);

  // Save to backend
  const saveInterests = async () => {
    setSaving(true);
    setMessage("");

    try {
      const res = await api.post("/user/interests/", {
        category_ids: selectedCategories,
        source_ids: selectedSources,
      });

      // Update saved snapshot
      setSavedCategories(res.data.categories ?? []);
      setSavedSources(res.data.sources ?? []);

      setMessage("Interests saved successfully!");
    } catch (err) {
      console.error(err);
      setMessage("Failed to save interests.");
    }

    setSaving(false);
  };

  if (loading)
    return <p className="text-gray-500 text-center mt-10">Loading...</p>;

  return (
    <div className="max-w-5xl mx-auto p-6">
      {/* Title */}
      <h1 className="text-2xl font-semibold mb-6">Customize Your Feed</h1>

      {/* Saved Interests Snapshot */}
      <div className="mb-10 p-4 rounded-lg border bg-gray-50 dark:bg-gray-800 dark:border-gray-700">
        <h2 className="text-lg font-medium mb-2 text-gray-800 dark:text-gray-200">Your Saved Interests</h2>

        <div className="mb-3">
          <span className="font-semibold text-gray-800 dark:text-gray-200">Categories:</span>{" "}
          {savedCategories.length > 0 ? (
            savedCategories.map((c) => (
              <span
                key={c.id}
                className="inline-block mx-1 px-2 py-1 bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-200 rounded-full text-sm"
              >
                {c.name}
              </span>
            ))
          ) : (
            <span className="text-gray-500 dark:text-gray-200">None selected</span>
          )}
        </div>

        <div>
          <span className="font-semibold text-gray-800 dark:text-gray-200">Sources:</span>{" "}
          {savedSources.length > 0 ? (
            savedSources.map((s) => (
              <span
                key={s.id}
                className="inline-block mx-1 px-2 py-1 bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-200 rounded-full text-sm"
              >
                {s.name}
              </span>
            ))
          ) : (
            <span className="text-gray-500 dark:text-gray-200" dark:text-gray-200>None selected</span>
          )}
        </div>
      </div>

      {/* Messages */}
      {message && (
        <div
          className={`mb-6 p-3 rounded-lg ${
            message.includes("success")
              ? "bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-200"
              : "bg-red-100 text-red-700 dark:bg-red-800 dark:text-red-200"
          }`}
        >
          {message}
        </div>
      )}

      {/* Category selection */}
      <section className="mb-10">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-xl font-medium text-red-600 dark:text-red-400">
            Select Categories
          </h2>

          <div className="flex gap-2">
            <button className="text-sm underline" onClick={selectAllCategories}>
              Select All
            </button>
            <button className="text-sm underline" onClick={clearAllCategories}>
              Clear All
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          {categories.map((cat) => {
            const active = selectedCategories.includes(cat.id);
            return (
              <button
                key={cat.id}
                onClick={() => toggleCategory(cat.id)}
                className={`px-4 py-2 rounded-full border transition font-medium ${
                  active
                    ? "bg-blue-600 text-white border-blue-600"
                    : "bg-white text-gray-800 border-gray-300 shadow-sm dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600"
                }`}
              >
                {cat.name}
              </button>
            );
          })}
        </div>
      </section>

      {/* Source selection */}
      <section className="mb-10">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-xl font-medium text-red-600 dark:text-red-400">
            Select Sources
          </h2>

          <div className="flex gap-2">
            <button className="text-sm underline" onClick={selectAllSources}>
              Select All
            </button>
            <button className="text-sm underline" onClick={clearAllSources}>
              Clear All
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          {sources.map((src) => {
            const active = selectedSources.includes(src.id);
            return (
              <button
                key={src.id}
                onClick={() => toggleSource(src.id)}
                className={`px-4 py-2 rounded-full border transition font-medium ${
                  active
                    ? "bg-blue-600 text-white border-blue-600"
                    : "bg-white text-gray-800 border-gray-300 shadow-sm dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600"
                }`}
              >
                {src.name}
              </button>
            );
          })}
        </div>
      </section>

      {/* Save */}
      <div className="flex justify-end">
        <button
          onClick={saveInterests}
          disabled={saving}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition disabled:opacity-60"
        >
          {saving ? "Saving..." : "Save Interests"}
        </button>
      </div>
    </div>
  );
};

export default Interests;
