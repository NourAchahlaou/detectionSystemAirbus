// import { AppBar, ThemeProvider, Toolbar, styled, useTheme } from "@mui/material";


// import useSettings from "app/hooks/useSettings";

// // STYLED COMPONENTS
// const AppFooter = styled(Toolbar)(() => ({
//   display: "flex",
//   alignItems: "center",
//   maxHeight: "30px" ,
//   "@media (max-width: 499px)": {
//     display: "table",
//     width: "100%",
//     maxHeight: "30px" ,
//     padding: "1rem 0",
//     "& .container": {
//       flexDirection: "column !important",
//       "& a": { margin: "0 0 16px !important" }
//     }
//   }
// }));

// const FooterContent = styled("div")(() => ({
//   width: "100%",
//   display: "flex",
//   alignItems: "center",
//   padding: "0px 1rem",
//   maxWidth: "1170px",
//   margin: "0 auto"
// }));

// export default function Footer() {
//   const theme = useTheme();
//   const { settings } = useSettings();

//   const footerTheme = settings.themes[settings.footer.theme] || theme;

//   return (
//     <ThemeProvider theme={footerTheme}>
//       <AppBar color="primary" position="static" sx={{ zIndex: 96 }}>
//         <AppFooter>
//           <FooterContent>

//           </FooterContent>
//         </AppFooter>
//       </AppBar>
//     </ThemeProvider>
//   );
// }
