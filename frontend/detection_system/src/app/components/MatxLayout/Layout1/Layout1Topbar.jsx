import { memo } from "react";
import { Link,useNavigate } from "react-router-dom";
import {
  Box,
  styled,
  Avatar,
  Hidden,
  useTheme,
  MenuItem,
  IconButton,
  useMediaQuery
} from "@mui/material";

import { NotificationProvider } from "app/contexts/NotificationContext";

import useAuth from "app/hooks/useAuth";
import useSettings from "app/hooks/useSettings";
import { useEffect, useState } from 'react';
import { Span } from "app/components/Typography";
import { MatxMenu } from "app/components";
import { NotificationBar } from "app/components/NotificationBar";
import { themeShadows } from "app/components/MatxTheme/themeColors";

import { topBarHeight } from "app/utils/constant";
import axios from "axios";
import {
  Home,
  Menu,
  Person,
  Settings,

  WebAsset,
  MailOutline,
  StarOutline,
  PowerSettingsNew
} from "@mui/icons-material";
import { User } from "@auth0/auth0-spa-js";
const styles = {
  container: {
    padding: '20px',
    maxWidth: '600px',
    margin: '0 auto',
    fontFamily: 'Arial, sans-serif',
  },
  title: {
    textAlign: 'center',
    marginBottom: '20px',
  },
  profile: {
    border: '1px solid #ddd',
    padding: '15px',
    borderRadius: '5px',
    backgroundColor: '#f9f9f9',
  },
  error: {
    color: 'red',
    textAlign: 'center',
    marginTop: '20px',
  },
  loading: {
    textAlign: 'center',
    fontSize: '18px',
  },
};

// STYLED COMPONENTS
const StyledIconButton = styled(IconButton)(({ theme }) => ({
  color: theme.palette.text.primary
}));

const TopbarRoot = styled("div")({
  top: 0,
  zIndex: 96,
  height: topBarHeight,
  boxShadow: themeShadows[8],
  transition: "all 0.3s ease"
});

const TopbarContainer = styled(Box)(({ theme }) => ({
  padding: "8px",
  paddingLeft: 18,
  paddingRight: 20,
  height: "100%",
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  background: theme.palette.primary.main,
  [theme.breakpoints.down("sm")]: { paddingLeft: 16, paddingRight: 16 },
  [theme.breakpoints.down("xs")]: { paddingLeft: 14, paddingRight: 16 }
}));

const UserMenu = styled(Box)({
  padding: 4,
  display: "flex",
  borderRadius: 24,
  cursor: "pointer",
  alignItems: "center",
  "& span": { margin: "0 8px" }
});

const StyledItem = styled(MenuItem)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  minWidth: 185,
  "& a": {
    width: "100%",
    display: "flex",
    alignItems: "center",
    textDecoration: "none"
  },
  "& span": { marginRight: "10px", color: theme.palette.text.primary }
}));

const IconBox = styled("div")(({ theme }) => ({
  display: "inherit",
  [theme.breakpoints.down("md")]: { display: "none !important" }
}));


const Layout1Topbar = () => {
  const theme = useTheme();
  const { settings, updateSettings } = useSettings();
  const { logout: authLogout } = useAuth();   // Import logout from your useAuth hook
  const isMdScreen = useMediaQuery(theme.breakpoints.down("md"));
  const navigate = useNavigate();   // Initialize the useNavigate hook

  const updateSidebarMode = (sidebarSettings) => {
    updateSettings({ layout1Settings: { leftSidebar: { ...sidebarSettings } } });
  };

  const handleSidebarToggle = () => {
    let { layout1Settings } = settings;
    let mode;
    if (isMdScreen) {
      mode = layout1Settings.leftSidebar.mode === "close" ? "mobile" : "close";
    } else {
      mode = layout1Settings.leftSidebar.mode === "full" ? "close" : "full";
    }
    updateSidebarMode({ mode });
  };

// Logout function
const handleLogout = async () => {
  try {
    // Retrieve the auth token
    const token = localStorage.getItem('token');

    // Call the backend logout endpoint
    const response = await axios.post(
      'http://127.0.0.1:8000/logout',
      {},  // You can pass an empty body if needed
      {
        headers: {
          Authorization: `Bearer ${token}`,  // Include the token in headers
        },
      }
    );

    // Check if the logout was successful
    if (response.status === 200) {
      // Remove the auth token from localStorage
      localStorage.removeItem('token');

      // Optionally, call authLogout (if needed in your hook)
      authLogout();

      // Redirect to the login page or home page
      navigate("/");
    } else {
      console.error("Logout failed", response.data);
    }
  } catch (error) {
    console.error("Error during logout:", error);
  }
};


  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) {
      setError('No authentication token found.');
      setLoading(false);
      return;
    }

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
    <TopbarRoot>
      <TopbarContainer>
        <Box display="flex">
          <StyledIconButton onClick={handleSidebarToggle}>
            <Menu />
          </StyledIconButton>
        </Box>

        <Box display="flex" alignItems="center">
          <NotificationProvider>
            <NotificationBar />
          </NotificationProvider>

          <MatxMenu
            menuButton={
              <UserMenu>
                <Hidden xsDown>
                  {userProfile ? (
                    <Span>
                      Hi <strong>{userProfile.firstName} {userProfile.secondName}</strong>
                    </Span>
                  ) : (
                    <p style={styles.error}>No profile data available.</p>
                  )}
                </Hidden>
                <Avatar sx={{ cursor: "pointer" }} />
              </UserMenu>
            }
          >
            <StyledItem>
              <Link to="/profile&Settings/profile">
                <Person />
                <Span>Profile</Span>
              </Link>
            </StyledItem>

            <StyledItem onClick={handleLogout}>
              <PowerSettingsNew />
              <Span>Logout</Span>
            </StyledItem>
          </MatxMenu>
        </Box>
      </TopbarContainer>
    </TopbarRoot>
  );
};

export default memo(Layout1Topbar);
