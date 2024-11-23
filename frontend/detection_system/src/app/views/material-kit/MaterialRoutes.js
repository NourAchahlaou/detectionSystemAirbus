import { lazy } from "react";
import Loadable from "app/components/Loadable";

const AppDefectHandling = Loadable(lazy(() => import("./imageAnnotaion/AppImageAnnotaion")));
const AppPartLibrary = Loadable(lazy(() => import("./partLibrary/AppPartLibrary")));
const AppInspection = Loadable(lazy(() => import("./inspection/AppInspection")));
const AppDatabasesetup = Loadable(lazy(() => import("./database/AppDatabasesetup")));
const AppProfile = Loadable(lazy(() => import("./profile/AppProfile")));
const AppIdentify = Loadable(lazy(() => import("./identifying/AppIdentify")));
const AppProfileSetting = Loadable(lazy(()=> import ("./profileSettings/AppProfileSettings")))
const Unauthorized = Loadable(lazy(()=> import ("../sessions/Unauthorized")))

const materialRoutes = [
  // { path: "/databaseSetup/database", element: <AppDatabasesetup /> },
  // { path: "/databaseSetup/imageAnnotaion", element: <AppDefectHandling /> },
  // { path: "/inspections/checkpieces", element: <AppInspection /> },
  { path: "/databaseSetup/captureimages", element: <AppPartLibrary /> },
  { path: "/profile&Settings/profile", element: <AppProfile /> },
  { path: "/inspections/identify", element: <AppIdentify /> },
  { path: "/unauthorized", element: <Unauthorized /> },
  // { path: "/profile&Settings/profileSettings", element : <AppProfileSetting/>},
];

export default materialRoutes;
