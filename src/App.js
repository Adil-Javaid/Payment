import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Login from "./Component/Login";
import AdminDashboard from "./Component/AdminDashboard";

const App = () => {
  const [isAdmin, setAdmin] = useState(false);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />

        <Route path="/login" element={<Login setAdmin={setAdmin} />} />

        <Route
          path="/dashboard"
          element={isAdmin ? <AdminDashboard isAdmin={isAdmin} /> : <Navigate to="/login" />}
        />
      </Routes>
    </Router>
  );
};

export default App;
