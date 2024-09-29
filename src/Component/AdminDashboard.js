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
      const response = await fetch("http://127.0.0.1:5000/transactions");
      if (!response.ok) throw new Error("Error fetching user data");
      const data = await response.json();
      setUsers(data);
      console.log(data); // Updated to log the fetched data
    } catch (error) {
      console.error("Error fetching user data:", error);
    }
  };

  const handleDepositAction = async (
    user_id,
    amount,
    transaction_id,
    action
  ) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/depositConfirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id, amount, transaction_id }),
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

    setSelectedUser({ user_id, amount, transaction_id });
    setModalType("deposit");
    setShowModal(true);
  };

  const handleWithdrawAction = async (user_id, amount, transaction_id) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/withdrawConfirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id, amount, transaction_id }),
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

    setSelectedUser({ user_id, amount, transaction_id });
    setModalType("withdraw");
    setShowModal(true);
  };

  const handleWithDrawDeclineAction = async (user_id, transaction_id) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/withdrawDecline", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id, transaction_id }),
      });

      const result = await response.json();
      if (response.ok) {
        alert(
          `Decline request for User ID: ${user_id}, Transaction ID: ${transaction_id}`
        );
        fetchUsers();
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error("Error declining request:", error);
      alert("Error processing the request.");
    }
  };

  const handleDepositDeclineAction = async (user_id, transaction_id) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/depositDecline", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id, transaction_id }),
      });

      const result = await response.json();
      if (response.ok) {
        alert(
          `Decline request for User ID: ${user_id}, Transaction ID: ${transaction_id}`
        );
        fetchUsers();
      } else {
        alert(`Error: ${result.message}`);
      }
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
            <th>Transaction Id</th>
            {/* <th>Username</th> */}
            {/* <th>Balance</th> */}
            <th>Amount</th>
            <th>Deposit Status</th>
            <th>Deposit Receipt</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) =>
            user.type === "deposit" ? (
              <tr key={user.transaction_id}>
                <td data-label="UserId">{user.user_id}</td>
                <td data-label="Transaction Id">{user.transaction_id}</td>
                {/* <td data-label="Username">{user.username}</td>
                <td data-label="Balance">{user.balance}</td> */}
                <td data-label="Amount">{user.amount}</td>
                <td data-label="Deposit Status">{user.status || "N/A"}</td>
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
                      handleDepositAction(
                        user.user_id,
                        user.amount,
                        user.transaction_id,
                        "approve"
                      )
                    }
                    disabled={user.status === "approved"}
                  >
                    Approve
                  </button>
                  <button
                    className="btn decline-btn"
                    onClick={() =>
                      handleDepositDeclineAction(
                        user.user_id,
                        user.transaction_id
                      )
                    }
                    disabled={user.status === "approved"}
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
            <th>Transaction Id</th>
            {/* <th>Username</th>
            <th>Balance</th> */}
            <th>Withdraw Amount</th>
            <th>Withdraw Status</th>
            <th>Account Number</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) =>
            user.type === "withdraw" ? (
              <tr key={user.transaction_id}>
                <td data-label="UserId">{user.user_id}</td>
                <td data-label="Transaction Id">{user.transaction_id}</td>
                <td data-label="Amount">{user.amount}</td>
                <td data-label="Withdraw Status">{user.status || "N/A"}</td>
                <td data-label="Account Number">{user.account_number}</td>
                <td>
                  <button
                    className="btn approve-btn"
                    onClick={() =>
                      handleWithdrawAction(
                        user.user_id,
                        user.amount, // Changed from user.withdraw to user.amount for consistency
                        user.transaction_id
                      )
                    }
                    disabled={user.status === "approved"}
                  >
                    Accept
                  </button>

                  <button
                    className="btn decline-btn"
                    onClick={() =>
                      handleWithDrawDeclineAction(
                        user.user_id,
                        user.transaction_id
                      )
                    }
                    disabled={user.status === "approved"}
                  >
                    Decline
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
