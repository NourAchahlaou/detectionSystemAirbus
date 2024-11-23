export const navigations = [
  // { name: "Dashboard", path: "/dashboard/default", icon: "dashboard" },
  
  { label: "Inspections", type: "label" },
  {
    name: "Inspections",
    icon: "image",
    badge: { value: "1", color: "secondary" },
    children: [
      { name: "Piece Validation", path: "/inspections/checkpieces", iconText: "P.V" },
      { name: "Piece Identification", path:"/inspections/identify", iconText: "P.I"}
    ]
  },
  { label: "Database Setup", type: "label" },
  {
    name: "Database Setup",
    icon: "data_usage",
    badge: { value: "3", color: "secondary" },
    children: [
      { name: "Database", path: "/databaseSetup/database", iconText: "C" },
      { name: "Image Annotation", path: "/databaseSetup/imageAnnotaion", iconText: "I.A" },
      { name: "Capture images", path: "/databaseSetup/captureimages", iconText: "C.I" }

    ]
  },


  

  { label: "Profile & Settings", type: "label" },
  {
    name: "Profile & Settings",
    icon: "account_circle",
    badge: { value: "2", color: "secondary" },
    children: [
      { name: "Profile", path: "/profile&Settings/profile", iconText: "P" },
      { name: "User Settings", path: "/profile&Settings/profileSettings", iconText: "U" },
    ]
  },

  
];
