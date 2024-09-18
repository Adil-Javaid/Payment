import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Modal from "./Modal";
import "./adminDashboard.css";

const AdminDashboard = ({ isAdmin }) => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAdmin) {
      navigate("/login");
    } else {
      fetchUsers();
    }
  }, [isAdmin, navigate]);

  const fetchUsers = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/users");
      if (!response.ok) throw new Error("Error fetching user data");
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error("Error fetching user data:", error);
    }
  };

  const handleDepositAction = async (user_id, amount, action) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/depositConfirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id, amount }), // Adjusted based on API
      });

      const result = await response.json();
      if (response.ok) {
        alert(`Deposit ${action} for User ID: ${user_id}`);
        fetchUsers(); // Refresh user data
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error("Error in deposit API:", error);
      alert("Error processing the request.");
    }

    setSelectedUser({ user_id, amount });
    setModalType("deposit");
    setShowModal(true);
  };

  const handleWithdrawAction = async (user_id, amount) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/withdrawConfirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id, amount }),
      });

      const result = await response.json();
      if (response.ok) {
        alert(`Withdraw accepted for User ID: ${user_id}`);
        fetchUsers(); // Refresh user data
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error("Error in withdraw API:", error);
      alert("Error processing the request.");
    }

    setSelectedUser({ user_id, amount });
    setModalType("withdraw");
    setShowModal(true);
  };

  const handleDeclineAction = async (user_id) => {
    try {
      // You may want to add logic here to decline the transaction
      alert(`Decline request for User ID: ${user_id}`);
      // Refresh user data if necessary
      fetchUsers();
    } catch (error) {
      console.error("Error declining request:", error);
      alert("Error processing the request.");
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedUser(null);
  };

  return (
    <div className="dashboard-container">
      <h2>Admin Dashboard</h2>

      <h3>Deposit Transactions</h3>
      <table className="responsive-table">
        <thead>
          <tr>
            <th>UserId</th>
            <th>Username</th>
            <th>Balance</th>
            <th>Deposit Amount</th>
            <th>Deposit Status</th>
            <th>Deposit Receipt</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) =>
            user.deposit_status === "pending" ? (
              <tr key={user.id}>
                <td data-label="UserId">{user.id}</td>
                <td data-label="Username">{user.username}</td>
                <td data-label="Balance">{user.balance}</td>
                <td data-label="Deposit Amount">{user.deposit}</td>
                <td data-label="Deposit Status">
                  {user.deposit_status || "N/A"}
                </td>
                <td data-label="Deposit Receipt">
                  {user.transaction_image ? (
                    <a
                      href={user.transaction_image}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Receipt
                    </a>
                  ) : (
                    "N/A"
                  )}
                </td>
                <td>
                  <button
                    className="btn approve-btn"
                    onClick={() =>
                      handleDepositAction(user.id, user.deposit, "approve")
                    }
                  >
                    Approve
                  </button>
                  <button
                    className="btn decline-btn"
                    onClick={() => handleDeclineAction(user.id)}
                  >
                    Decline
                  </button>
                </td>
              </tr>
            ) : null
          )}
        </tbody>
      </table>

      <h3>Withdraw Transactions</h3>
      <table className="responsive-table">
        <thead>
          <tr>
            <th>UserId</th>
            <th>Username</th>
            <th>Balance</th>
            <th>Withdraw Amount</th>
            <th>Withdraw Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) =>
            user.withdraw_status === "pending" ? (
              <tr key={user.id}>
                <td data-label="UserId">{user.id}</td>
                <td data-label="Username">{user.username}</td>
                <td data-label="Balance">{user.balance}</td>
                <td data-label="Withdraw Amount">{user.withdraw}</td>
                <td data-label="Withdraw Status">
                  {user.withdraw_status || "N/A"}
                </td>
                <td>
                  <button
                    className="btn approve-btn"
                    onClick={() => handleWithdrawAction(user.id, user.withdraw)}
                  >
                    Accept
                  </button>
                </td>
              </tr>
            ) : null
          )}
        </tbody>
      </table>

      <Modal
        show={showModal}
        onClose={closeModal}
        userId={selectedUser?.user_id}
        amount={selectedUser?.amount}
        type={modalType}
      />
    </div>
  );
};

export default AdminDashboard;
