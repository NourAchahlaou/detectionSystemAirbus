import { useEffect, useState } from 'react';
import axios from 'axios';
import DataTable from './DataTableProfile';
import { Breadcrumb } from "app/components";
import { Box, styled } from "@mui/material";

// Updated Component Styles (similar to AdminUserSettings)
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
  profileContainer: {
    background: '#ffffff',
    borderRadius: '10px',
    padding: '20px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
    marginBottom: '30px',
  },
  profileInfo: {
    padding: '15px',
    borderRadius: '5px',
    backgroundColor: '#f9f9f9',
    borderBottom: '1px solid #ddd',
  },
  profileField: {
    marginBottom: '15px',
    fontSize: '16px',
    color: '#555',
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
  tableContainer: {
    marginTop: '30px',
    padding: '20px',
    borderRadius: '10px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
    backgroundColor: '#ffffff',
  }
};

// Styled component for Container
const Container = styled("div")(({ theme }) => ({
  margin: "30px",
  [theme.breakpoints.down("sm")]: { margin: "16px" },
  "& .breadcrumb": {
    marginBottom: "30px",
    [theme.breakpoints.down("sm")]: { marginBottom: "16px" }
  }
}));

function UserProfile() {
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Retrieve the token from local storage
  const token = localStorage.getItem('authToken');

  useEffect(() => {
    if (!token) {
      setError('No authentication token found.');
      setLoading(false);
      return;
    }

    // Fetch user profile from the backend
    axios
      .get('http://127.0.0.1:8000/users/profile', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {
        setUserProfile(response.data);
        setLoading(false);
      })
      .catch((err) => {
        const errorMessage = err.response?.data?.detail || 'Failed to load profile data.';
        setError(errorMessage);
        setLoading(false);
      });
  }, [token]);

  if (loading) return <p style={styles.loading}>Loading...</p>;
  if (error) return <p style={styles.error}>{error}</p>;

  return (
    <Container>
      <Box className="breadcrumbs">
        <Breadcrumb routeSegments={[{ name: "Profile Settings" }]} />
      </Box>
      <div style={styles.container}>
        <h1 style={styles.title}>User Profile</h1>
        <div style={styles.profileContainer}>
          {userProfile ? (
            <>
              <div style={styles.profileInfo}>
                <p style={styles.profileField}><strong>User ID:</strong> {userProfile.user_id}</p>
                <p style={styles.profileField}><strong>First Name:</strong> {userProfile.firstName}</p>
                <p style={styles.profileField}><strong>Last Name:</strong> {userProfile.secondName}</p>
                <p style={styles.profileField}><strong>Email:</strong> {userProfile.email}</p>
                <p style={styles.profileField}><strong>Role:</strong> {userProfile.role_id === 1 ? 'Admin' : 'Quality Specialist'}</p>
              </div>
            </>
          ) : (
            <p style={styles.error}>No profile data available.</p>
          )}
        </div>

        {/* DataTable component with enhanced styling */}
        <div style={styles.tableContainer}>
          
          <DataTable user_id={userProfile.user_id} />
        </div>
      </div>
    </Container>
  );
}

export default UserProfile;
