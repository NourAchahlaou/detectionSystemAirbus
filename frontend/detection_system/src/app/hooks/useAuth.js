import { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

const useAuth = () => {
  const [authState, setAuthState] = useState({
    token: localStorage.getItem("authToken") || null,
    error: null,
    loading: false,
  });
  
  const login = async (username, password) => {
    setAuthState((prevState) => ({ ...prevState, loading: true }));
    
    try {
      const response = await axios.post(
        `${API_URL}/token`,
        new URLSearchParams({ username, password }),
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      );
      
      const { access_token } = response.data;
      console.log("Login response:", response);
      
      // Store token in localStorage and update authState
      localStorage.setItem("authToken", access_token);
      setAuthState({ token: access_token, error: null, loading: false });
      
      return response.data; // Return the token data
    } catch (error) {
      console.error("Login error:", error);
      setAuthState({ token: null, error: error.message, loading: false });
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    setAuthState({ token: null, error: null, loading: false });
  };

  const isAuthenticated = Boolean(authState.token); // Check if token exists

  return { ...authState, login, logout, isAuthenticated };
};

export default useAuth;
