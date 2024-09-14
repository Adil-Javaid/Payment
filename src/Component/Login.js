// components/Login.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";

const Login = ({ setAdmin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();

    const adminEmail = "adil@gmail.com";
    const adminPassword = "adil123";

    if (email === adminEmail && password === adminPassword) {
      setAdmin(true);
      navigate("/dashboard");
    } else {
      setError("Invalid credentials!");
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Admin Login</h2>
        {error && <p>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit">Sign In</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
