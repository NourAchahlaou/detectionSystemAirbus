import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '20px auto',
    fontFamily: "'Roboto', sans-serif",
  },
  title: {
    textAlign: 'center',
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '20px',
  },
  formContainer: {
    background: '#ffffff',
    borderRadius: '10px',
    padding: '20px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
    marginBottom: '30px',
  },
  tableContainer: {
    width: '100%',
    overflowX: 'auto',
    marginBottom: '30px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  tableHeader: {
    backgroundColor: '#f5f5f5',
    fontWeight: 'bold',
  },
  tableRow: {
    textAlign: 'center',
  },
  tableCell: {
    padding: '12px',
    borderBottom: '1px solid #ddd',
  },
  button: {
    margin: '0 5px',
    padding: '8px 14px',
    border: 'none',
    cursor: 'pointer',
    borderRadius: '5px',
    fontSize: '14px',
  },
  addButton: {
    backgroundColor: '#4CAF50',
    color: 'white',
  },
  editButton: {
    backgroundColor: '#FF8C00',
    color: 'white',
  },
  deleteButton: {
    backgroundColor: '#FF6347',
    color: 'white',
  },
  form: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '15px',
  },
  input: {
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '5px',
    width: '100%',
  },
  select: {
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '5px',
    backgroundColor: '#f9f9f9',
  },
  error: {
    color: '#FF6347',
    textAlign: 'center',
    marginTop: '20px',
  },
  loading: {
    textAlign: 'center',
    fontSize: '18px',
  },
  paginationButton: {
    margin: '0 5px',
    padding: '10px 16px',
    border: '1px solid #ddd',
    backgroundColor: '#007bff',
    color: 'white',
    cursor: 'pointer',
    borderRadius: '30px',
    fontSize: '14px',
    transition: 'all 0.3s ease-in-out',
    outline: 'none',
  },
  paginationButtonDisabled: {
    backgroundColor: '#cccccc',
    color: '#666666',
    cursor: 'not-allowed',
    border: '1px solid #ccc',
  },
  paginationButtonHover: {
    backgroundColor: '#0056b3',
    color: '#ffffff',
  },

  modal: {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%) scale(1)',
    background: 'linear-gradient(145deg, #ffffff, #e6e6e6)',
    padding: '30px 40px',
    boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
    zIndex: 1000,
    borderRadius: '15px',
    width: '350px',
    textAlign: 'center',
    opacity: 0,
    animation: 'fadeIn 0.3s ease-in-out forwards',
  },
  
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    backdropFilter: 'blur(4px)',
    zIndex: 999,
    opacity: 0,
    animation: 'fadeOverlay 0.3s ease-in-out forwards',
  },
  
  modalButton: {
    margin: '10px',
    padding: '12px 25px',
    cursor: 'pointer',
    borderRadius: '30px',
    border: 'none',
    boxShadow: '0 5px 10px rgba(0,0,0,0.15)',
    transition: 'transform 0.2s ease-in-out',
  },
  
  confirmButton: {
    backgroundColor: '#28a745',
    color: 'white',
    '&:hover': {
      transform: 'scale(1.05)',
    },
  },
  
  cancelButton: {
    backgroundColor: '#ff4757',
    color: 'white',
    '&:hover': {
      transform: 'scale(1.05)',
    },
  },
  
};

// Role mapping from ID to descriptive text
const roleMapping = {
  1: 'Admin',
  2: 'Quality Specialist',
  // Add other role mappings as needed
};

function AdminUserSettings() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editUser, setEditUser] = useState(null);
  const [showModal, setShowModal] = useState(false); // Modal state
  const [modalMessage, setModalMessage] = useState(''); // Modal message
  const [deleteUserId, setDeleteUserId] = useState(null); // User to be deleted
  const [formData, setFormData] = useState({
    user_id: '',
    firstName: '',
    secondName: '',
    email: '',
    password: '',
    role: 'quality specialist',
  });

  const [currentPage, setCurrentPage] = useState(1);
  const usersPerPage = 4;

  const token = localStorage.getItem('authToken');

  // Fetch users function
  const fetchUsers = useCallback(async () => {
    if (!token) {
      showErrorModal('No authentication token found.');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get('http://127.0.0.1:8000/users/users', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsers(response.data);
    } catch (err) {
      showErrorModal(err.response?.data?.detail || 'Failed to load users.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const totalPages = Math.ceil(users.length / usersPerPage);
  const currentUsers = users.slice((currentPage - 1) * usersPerPage, currentPage * usersPerPage);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    const payload = {
      user_id: formData.user_id,
      firstName: formData.firstName,
      secondName: formData.secondName,
      email: formData.email || null, // If no email, send null
      password: formData.password,
      role: { roleType: formData.role },
    };
  
    try {
      await axios.post('http://127.0.0.1:8000/users/createUser', payload, {
        headers: { Authorization: `Bearer ${token}` },
      });
      resetForm();
      fetchUsers();
    } catch (err) {
      console.log("Error Response:", err.response);  // Log full error response
      const errorMessage = err.response?.data?.detail || 'Unexpected server error occurred';
      showErrorModal(errorMessage);
    }
  };
  
  

  const handleEditUser = async (e) => {
    e.preventDefault();
    const payload = {
      user_id: formData.user_id,
      firstName: formData.firstName,
      secondName: formData.secondName,
      email: formData.email,
      password: formData.password,
      role: { roleType: formData.role },
    };

    try {
      const response = await axios.put(`http://127.0.0.1:8000/users/updateUser/${editUser.user_id}`, payload, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsers(users.map((user) => (user.user_id === response.data.user_id ? response.data : user)));
      resetForm();
    } catch (err) {
      showErrorModal(err.response?.data?.detail || 'Failed to update user.');
    }
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`http://127.0.0.1:8000/users/deleteProfile/${deleteUserId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsers(users.filter((user) => user.user_id !== deleteUserId));
      setDeleteUserId(null);
      setShowModal(false);
    } catch (err) {
      showErrorModal(err.response?.data?.detail || 'Failed to delete user.');
    }
  };
  const handlePreviousPage = () => setCurrentPage((prevPage) => Math.max(prevPage - 1, 1));
  const handleNextPage = () => setCurrentPage((prevPage) => Math.min(prevPage + 1, totalPages));

  const resetForm = () => {
    setFormData({ user_id: '', firstName: '', secondName: '', email: '', password: '', role: 'quality specialist' });
    setEditUser(null);
  };

  const showErrorModal = (message) => {
    setModalMessage(message);
    setShowModal(true);
  };

  const handleEditClick = (user) => {
    setFormData({
      user_id: user.user_id,
      firstName: user.firstName,
      secondName: user.secondName,
      email: user.email,
      password: '', // Password should remain blank initially
      role: user.role_id === 1 ? 'admin' : 'quality specialist',
    });
    setEditUser(user);
  };

  if (loading) return <p style={styles.loading}>Loading...</p>;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}> User Settings</h1>
      <style>
        {`
          @keyframes fadeIn {
            from {
              opacity: 0;
              transform: translate(-50%, -50%) scale(0.9);
            }
            to {
              opacity: 1;
              transform: translate(-50%, -50%) scale(1);
            }
          }

          @keyframes fadeOverlay {
            from {
              opacity: 0;
            }
            to {
              opacity: 1;
            }
          }
        `}
      </style>
      {showModal && (
        
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <p>{modalMessage}</p>
            {deleteUserId ? (
              <div>
                <button onClick={handleDelete} style={{ ...styles.modalButton, ...styles.confirmButton }}>Confirm</button>
                <button onClick={() => setShowModal(false)} style={{ ...styles.modalButton, ...styles.cancelButton }}>Cancel</button>
              </div>
            ) : (
              <button onClick={() => setShowModal(false)} style={styles.modalButton}>Close</button>
            )}
          </div>
        </div>
      )}
      
      <div style={styles.formContainer}>
        <form style={styles.form} onSubmit={editUser ? handleEditUser : handleAddUser}>
          {/* Form Inputs */}
          <input type="text" name="user_id" placeholder="User ID" style={styles.input} value={formData.user_id} onChange={handleInputChange} required />
          <input type="text" name="firstName" placeholder="First Name" style={styles.input} value={formData.firstName} onChange={handleInputChange} required />
          <input type="text" name="secondName" placeholder="Last Name" style={styles.input} value={formData.secondName} onChange={handleInputChange} required />
          <input
            type="email"
            name="email"
            placeholder="Email (optional)"
            style={styles.input}
            value={formData.email}
            onChange={handleInputChange}
          />
          <input type="password" name="password" placeholder="Password" style={styles.input} value={formData.password} onChange={handleInputChange} required />
          <select name="role" style={styles.select} value={formData.role} onChange={handleInputChange}>
            <option value="admin">Admin</option>
            <option value="quality specialist">Quality Specialist</option>
          </select>

          {/* Add/Edit and Cancel Buttons */}
          <div>
            <button type="submit" style={{ ...styles.button, ...(editUser ? styles.editButton : styles.addButton) }}>
              {editUser ? 'Update User' : 'Add User'}
            </button>
            {editUser && (
              <button type="button" onClick={resetForm} style={{ ...styles.button, ...styles.cancelButton }}>
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>
      <div style={styles.tableContainer}>
        <table style={styles.table}>
          <thead style={styles.tableHeader}>
            <tr>
              <th style={styles.tableCell}>User ID</th>
              <th style={styles.tableCell}>First Name</th>
              <th style={styles.tableCell}>Last Name</th>
              <th style={styles.tableCell}>Email</th>
              <th style={styles.tableCell}>Role</th>
              <th style={styles.tableCell}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {currentUsers.map((user) => (
              <tr key={user.user_id} style={styles.tableRow}>
                <td style={styles.tableCell}>{user.user_id}</td>
                <td style={styles.tableCell}>{user.firstName}</td>
                <td style={styles.tableCell}>{user.secondName}</td>
                <td style={styles.tableCell}>{user.email}</td>
                <td style={styles.tableCell}>{roleMapping[user.role_id]}</td>
                <td style={styles.tableCell}>
                  <button style={{ ...styles.button, ...styles.editButton }} onClick={() => setEditUser(user)}>
                    Edit
                  </button>
                  <button style={{ ...styles.button, ...styles.deleteButton }} onClick={() => handleDelete(user.user_id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
           {/* Pagination Controls */}
           <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '20px' }}>
        <button
          onClick={handlePreviousPage}
          disabled={currentPage === 1}
          style={{
            margin: '0 5px',
            padding: '8px 14px',
            border: '1px solid #ddd',
            backgroundColor: currentPage === 1 ? '#cccccc' : '#007bff',
            color: currentPage === 1 ? '#666666' : 'white',
            cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
            borderRadius: '5px',
            fontSize: '14px',
          }}
        >
          &lt;
        </button>
        <span style={{ margin: '0 10px', fontSize: '16px' }}>
          Page {currentPage} of {totalPages}
        </span>
        <button
          onClick={handleNextPage}
          disabled={currentPage === totalPages}
          style={{
            margin: '0 5px',
            padding: '8px 14px',
            border: '1px solid #ddd',
            backgroundColor: currentPage === totalPages ? '#cccccc' : '#007bff',
            color: currentPage === totalPages ? '#666666' : 'white',
            cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
            borderRadius: '5px',
            fontSize: '14px',
          }}
        >
          &gt;
        </button>
      </div>

      {/* Pagination Controls */}
      {/* <div style={styles}>
        <button
          style={{ ...styles.paginationButton, ...(currentPage === 1 && styles.paginationButtonDisabled) }}
          onClick={handlePreviousPage}
          disabled={currentPage === 1}
        >
          Previous
        </button>
        <span style={{ margin: '0 10px' }}>
          Page {currentPage} of {totalPages}
        </span>
        <button
          style={{ ...styles.paginationButton, ...(currentPage === totalPages && styles.paginationButtonDisabled) }}
          onClick={handleNextPage}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div> */}
    </div>
  );
}

export default AdminUserSettings;
