import { Fragment } from "react";
import {  Grid, styled } from "@mui/material";


// STYLED COMPONENTS
const ContentBox = styled("div")(({ theme }) => ({
  margin: "30px",
  [theme.breakpoints.down("sm")]: { margin: "16px" }
}));



export default function Analytics() {
 

  return (
    <Fragment>
      <ContentBox className="analytics">
        <Grid container spacing={3}>

        </Grid>
      </ContentBox>
    </Fragment>
  );
}
