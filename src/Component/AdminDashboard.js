import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Modal from "./Modal"; // Import the Modal component
import "./adminDashboard.css"; // Import CSS file

const AdminDashboard = ({ isAdmin }) => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(""); // "deposit" or "withdraw"
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

  const handleDepositAction = (userId, amount, action) => {
    if (action === "approve" || action === "decline") {
      setSelectedUser({ userId, amount });
      setModalType("deposit");
      setShowModal(true);
    }
  };

  const handleWithdrawAction = (userId, amount) => {
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

      {/* Deposit Transactions */}
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
                  <td>{user.userId}</td>
                  <td>{user.userName}</td>
                  <td>{user.userPassword}</td>
                  <td>{user.balance}</td>
                  <td>{user.deposit.amount}</td>
                  <td>{user.deposit.status || "N/A"}</td>
                  <td>
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
                      onClick={() => (alert('Amount Decline'))
                      }
                    >
                      Decline
                    </button>
                  </td>
                </tr>
              )
          )}
        </tbody>
      </table>

      {/* Withdraw Transactions */}
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
                  <td>{user.userId}</td>
                  <td>{user.userName}</td>
                  <td>{user.userPassword}</td>
                  <td>{user.balance}</td>
                  <td>{user.withdrawal.amount}</td>
                  <td>{user.withdrawal.status || "N/A"}</td>
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

      {/* Modal Popup for Deposit/Withdraw Details */}
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
