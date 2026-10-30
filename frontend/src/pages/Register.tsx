import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { API_URL } from "../api/api"; // for debugging if needed

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    console.log("🧾 Sending registration request:", {
      username,
      email,
      password,
    });
    console.log("🔗 Register endpoint:", `${API_URL}/register/`);

    try {
      // Step 1️⃣ - Create the new user via Django endpoint
      await registerUser(username, email, password);

      // Step 2️⃣ - Immediately log the user in
      await login(username, password);

      navigate("/feed");
    } catch (err: any) {
      console.error("❌ Registration failed:", err.response?.data || err);
      alert("Registration failed. Please check your details.");
    }
  };

  return (
    <div className="flex flex-col items-center mt-10">
      <h1 className="text-2xl font-bold mb-4">Register</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-64">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="border p-2 rounded"
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border p-2 rounded"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-2 rounded"
        />
        <button
          type="submit"
          className="bg-green-500 text-white rounded p-2 hover:bg-green-600"
        >
          Register
        </button>
      </form>
    </div>
  );
}
