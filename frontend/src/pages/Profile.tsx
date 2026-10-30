import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api/api";

interface ProfileData {
  id: number;
  username: string;
  email: string;
  date_joined?: string;
}

const Profile: React.FC = () => {
  const { user, accessToken } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(user);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!accessToken || profile) return;
      try {
        setLoading(true);
        const res = await api.get("/user/");
        setProfile(res.data);
      } catch (err) {
        console.error("❌ Failed to load profile:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [accessToken, profile]);

  if (loading) return <p className="text-center mt-10">Loading profile...</p>;

  if (!profile)
    return <p className="text-center mt-10">No user profile found.</p>;

  return (
    <div className="max-w-lg mx-auto bg-white shadow-md rounded-2xl p-8 mt-10">
      <h1 className="text-2xl font-semibold mb-4 text-gray-800 text-center">
        👤 User Profile
      </h1>
      <div className="space-y-3 text-gray-700">
        <p>
          <strong>Username:</strong> {profile.username}
        </p>
        <p>
          <strong>Email:</strong> {profile.email}
        </p>
        {profile.date_joined && (
          <p>
            <strong>Joined:</strong>{" "}
            {new Date(profile.date_joined).toLocaleDateString()}
          </p>
        )}
      </div>
    </div>
  );
};

export default Profile;
