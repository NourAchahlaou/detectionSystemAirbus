import { createContext, useEffect, useReducer } from "react";
import axios from "axios";
import { MatxLoading } from "app/components";

const initialState = {
  user: null,
  isInitialized: false,
  isAuthenticated: false
};

const reducer = (state, action) => {
  switch (action.type) {
    case "INIT": {
      const { isAuthenticated, user } = action.payload;
      return { ...state, isAuthenticated, isInitialized: true, user };
    }

    case "LOGIN": {
      return { ...state, isAuthenticated: true, user: action.payload.user };
    }

    case "LOGOUT": {
      return { ...state, isAuthenticated: false, user: null };
    }

    case "REGISTER": {
      const { user } = action.payload;
      return { ...state, isAuthenticated: true, user };
    }

    default:
      return state;
  }
};

const AuthContext = createContext({
  ...initialState,
  method: "JWT",
  login: () => {},
  logout: () => {},
  register: () => {}
});

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  const login = async (user_id, password) => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/token", new URLSearchParams({
        user_id: user_id,
        password: password
      }).toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      const { access_token } = response.data;

      // Store token
      localStorage.setItem("authToken", access_token);

      // Fetch user profile
      const profileResponse = await axios.get("http://127.0.0.1:8000/users/profile", {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      });
      const user = profileResponse.data; // Ensure this contains role_id

      dispatch({ type: "LOGIN", payload: { user } });
    } catch (error) {
      console.error('Login failed', error);
      throw error;
    }
  };

  const register = async (email, username, password) => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/users/createUser", { email, username, password });
      const { user } = response.data;

      dispatch({ type: "REGISTER", payload: { user } });
    } catch (error) {
      console.error('Registration failed', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    dispatch({ type: "LOGOUT" });
  };

  useEffect(() => {
    (async () => {
      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          dispatch({ type: "INIT", payload: { isAuthenticated: false, user: null } });
          return;
        }
        
        // Try to fetch the user profile
        const { data } = await axios.get("http://127.0.0.1:8000/users/profile", {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        dispatch({ type: "INIT", payload: { isAuthenticated: true, user: data } });
      } catch (err) {
        console.error(err);
        dispatch({ type: "INIT", payload: { isAuthenticated: false, user: null } });
      }
    })();
  }, []);

  // SHOW LOADER
  if (!state.isInitialized) return <MatxLoading />;

  return (
    <AuthContext.Provider value={{ ...state, method: "JWT", login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
