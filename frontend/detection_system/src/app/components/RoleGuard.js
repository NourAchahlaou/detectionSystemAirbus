// components/RoleGuard.js

import { Navigate } from "react-router-dom";
import { useContext } from "react";
import AuthContext from "../contexts/JWTAuthContext";

const RoleGuard = ({ children, allowedRoles }) => {
  const { user } = useContext(AuthContext);

  // if (!user) {
  //   return <Navigate to="/signin" />;
  // }

  if (!allowedRoles.includes(user.role_id)) {
    return <Navigate to="/unauthorized" />;
  }
  else if (!user || user.role_id == null) {
    return <Navigate to="/signin" />;
  }
  

  return children;
};

export default RoleGuard;
