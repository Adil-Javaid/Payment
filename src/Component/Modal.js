import React from "react";
import "./modal.css";

const Modal = ({ show, onClose, userId, amount, type }) => {
  if (!show) {
    return null;
  }

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <h3>{type === "deposit" ? "Deposit Details" : "Withdraw Details"}</h3>
        <p><strong>User ID:</strong> {userId}</p>
        <p><strong>{type === "deposit" ? "Deposit Amount" : "Withdraw Amount"}:</strong> {amount}</p>
        <button className="close-btn" onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default Modal;
