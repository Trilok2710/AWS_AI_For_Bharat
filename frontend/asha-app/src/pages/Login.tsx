import React, { useState } from "react";
import Header from "../components/Header";
import Button from "../components/Button";
import { login } from "../services/api";

interface LoginProps {
  onLoginSuccess: (asha: any) => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [phone, setPhone] = useState("");
  const [pin, setPin] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await login(phone, pin);
      onLoginSuccess(response.asha);
    } catch (err: any) {
      setError("Invalid phone number or PIN.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header title="MediConnect" subtitle="ASHA Worker Login" />

      <div className="max-w-md mx-auto px-4 mt-10">
        <div className="bg-white border border-gray-200 p-6">

          <div className="space-y-4">
            {/* Phone Input */}
            <div>
              <label className="block text-sm font-medium text-textPrimary mb-1">
                Phone Number
              </label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full border border-gray-300 px-3 py-2 text-sm focus:outline-none"
                placeholder="+919876543210"
              />
            </div>

            {/* PIN Input */}
            <div>
              <label className="block text-sm font-medium text-textPrimary mb-1">
                PIN
              </label>
              <input
                type="password"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                className="w-full border border-gray-300 px-3 py-2 text-sm focus:outline-none"
                placeholder="Enter 4-digit PIN"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="text-sm text-emergency">
                {error}
              </div>
            )}

            {/* Login Button */}
            <Button
              label={loading ? "Logging in..." : "Login"}
              onClick={handleLogin}
              variant="primary"
              disabled={loading}
            />
          </div>

        </div>
      </div>
    </div>
  );
};

export default Login;