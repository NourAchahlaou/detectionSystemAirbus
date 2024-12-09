import { Navigate, useLocation } from "react-router-dom";
import useAuth from "app/hooks/useAuth";
import { useContext } from "react";
import AuthContext from "../contexts/JWTAuthContext";

export default function AuthGuard({ children }) {
  const { token, isAuthenticated } = useAuth();
  const { pathname } = useLocation();
  const { user } = useContext(AuthContext);

  // if (!user) {
  //   return <Navigate to="/signin" />;
  // }


  if (!user || user.role_id == null) {
    return <Navigate to="/signin" />;
  }
  else if (!token || !isAuthenticated) {
    return <Navigate to="/signin" />;
  }
  else if (isAuthenticated && token) {
    return <>{children}</>;
  }

  // Redirect unauthenticated users to sign-in page
  return <Navigate replace to="/signin" state={{ from: pathname }} />;
}
