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
    }

    fetch("/Data/userData.json")
      .then((res) => res.json())
      .then((data) => setUsers(data))
      .catch((error) => console.error("Error fetching user data:", error));
  }, [isAdmin, navigate]);

  const handleDepositAction = async (userId, amount, action) => {
    try {
      const response = await fetch("/api/deposit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ userId, amount, action }),
      });

      const result = await response.json();
      if (response.ok) {
        alert(`Deposit ${action} for User ID: ${userId}`);
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error("Error in deposit API:", error);
      alert("Error processing the request.");
    }

    setSelectedUser({ userId, amount });
    setModalType("deposit");
    setShowModal(true);
  };

  const handleWithdrawAction = async (userId, amount) => {
    try {
      const response = await fetch("/api/withdraw", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ userId, amount }),
      });

      const result = await response.json();
      if (response.ok) {
        alert(`Withdraw accepted for User ID: ${userId}`);
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error("Error in withdraw API:", error);
      alert("Error processing the request.");
    }

    setSelectedUser({ userId, amount });
    setModalType("withdraw");
    setShowModal(true);
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
            <th>User Password</th>
            <th>Balance</th>
            <th>Deposit Amount</th>
            <th>Deposit Status</th>
            <th>Deposit Receipt</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map(
            (user) =>
              user.deposit.status === "pending" && (
                <tr key={user.userId}>
                  <td data-label="UserId">{user.userId}</td>
                  <td data-label="Username">{user.userName}</td>
                  <td data-label="User Password">{user.userPassword}</td>
                  <td data-label="Balance">{user.balance}</td>
                  <td data-label="Deposit Amount">{user.deposit.amount}</td>
                  <td data-label="Deposit Status">
                    {user.deposit.status || "N/A"}
                  </td>
                  <td data-label="Deposit Receipt">
                    {user.deposit.image ? (
                      <a
                        href={user.deposit.image}
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
                        handleDepositAction(
                          user.userId,
                          user.deposit.amount,
                          "approve"
                        )
                      }
                    >
                      Approve
                    </button>
                    <button
                      className="btn decline-btn"
                      onClick={() => alert("Decline")}
                    >
                      Decline
                    </button>
                  </td>
                </tr>
              )
          )}
        </tbody>
      </table>

      <h3>Withdraw Transactions</h3>
      <table className="responsive-table">
        <thead>
          <tr>
            <th>UserId</th>
            <th>Username</th>
            <th>User Password</th>
            <th>Balance</th>
            <th>Withdraw Amount</th>
            <th>Withdraw Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map(
            (user) =>
              user.withdrawal.status === "pending" && (
                <tr key={user.userId}>
                  <td data-label="User Id">{user.userId}</td>
                  <td data-label="User Name">{user.userName}</td>
                  <td data-label="User Password">{user.userPassword}</td>
                  <td data-label="User Balance">{user.balance}</td>
                  <td data-label="User Withdraw">{user.withdrawal.amount}</td>
                  <td data-label="User Withdraw Status">
                    {user.withdrawal.status || "N/A"}
                  </td>
                  <td>
                    <button
                      className="btn approve-btn"
                      onClick={() =>
                        handleWithdrawAction(
                          user.userId,
                          user.withdrawal.amount
                        )
                      }
                    >
                      Accept
                    </button>
                  </td>
                </tr>
              )
          )}
        </tbody>
      </table>

      <Modal
        show={showModal}
        onClose={closeModal}
        userId={selectedUser?.userId}
        amount={selectedUser?.amount}
        type={modalType}
      />
    </div>
  );
};

export default AdminDashboard;
