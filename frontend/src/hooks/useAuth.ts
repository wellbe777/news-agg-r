import { useState } from "react";

// 🔹 Replace with real backend auth later
export default function useAuth() {
  const [user, setUser] = useState<{ username: string } | null>(
    localStorage.getItem("user")
      ? { username: localStorage.getItem("user") as string }
      : null
  );

  function login(username: string) {
    localStorage.setItem("user", username);
    setUser({ username });
  }

  function logout() {
    localStorage.removeItem("user");
    setUser(null);
  }

  return { user, login, logout };
}
