import { lazy } from "react";
import { Navigate } from "react-router-dom";
import AuthGuard from "./auth/AuthGuard";
import RoleGuard from "./components/RoleGuard"; // Import the RoleGuard
import Loadable from "./components/Loadable";
import MatxLayout from "./components/MatxLayout/MatxLayout";
import materialRoutes from "app/views/material-kit/MaterialRoutes";

// SESSION PAGES
const NotFound = Loadable(lazy(() => import("app/views/sessions/NotFound")));
const NoData = Loadable(lazy(() => import("app/views/sessions/NoData")));
const JwtLogin = Loadable(lazy(() => import("app/views/sessions/JwtLogin")));
const AppInspection = Loadable(lazy(() => import("app/views/material-kit/inspection/AppInspection")));
const AppDefectHandling = Loadable(lazy(() => import("app/views/material-kit/imageAnnotaion/AppImageAnnotaion")));
const AppDatabasesetup = Loadable(lazy(() => import("app/views/material-kit/database/AppDatabasesetup")));
const AppProfileSetting = Loadable(lazy(() => import("app/views/material-kit/profileSettings/AppProfileSettings")));
const AppPartLibrary = Loadable(lazy(() => import("app/views/material-kit/partLibrary/AppPartLibrary")));

const routes = [
  {
    element: (
      <AuthGuard>
        <MatxLayout />
      </AuthGuard>
    ),
    children: [
      { path: "/databaseSetup/captureimages",
         element:
         (
          <RoleGuard allowedRoles={[1]}>
            <AppPartLibrary />
          </RoleGuard>
        )  
      },

      // Protect routes based on roles
      { 
        path: "/databaseSetup/database", 
        element: (
          <RoleGuard allowedRoles={[1]}>
            <AppDatabasesetup />
          </RoleGuard>
        ) 
      },
      { 
        path: "/databaseSetup/imageAnnotaion", 
        element: (
          
            <AppDefectHandling />
         
        ) 
      },
      { 
        path: "/inspections/checkpieces", 
        element: (
         
            <AppInspection />
          
        ) 
      },

      { 
        path: "/profile&Settings/profileSettings", 
        element: (
          <RoleGuard allowedRoles={[1]}>
            <AppProfileSetting />
          </RoleGuard>
        ) 
      },
      ...materialRoutes, // Include other material routes here
    ]
  },

  // session pages route
  { path: "/404", element: <NotFound /> },
  { path: "/204", element: <NoData /> },
  { path: "/signin", element: <JwtLogin /> },
  { path: "/", element: <Navigate to="/profile&Settings/profile" /> },
  { path: "*", element: <NotFound /> }
];

export default routes;
