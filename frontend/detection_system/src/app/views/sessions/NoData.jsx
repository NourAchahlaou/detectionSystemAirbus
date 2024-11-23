import { Box, Button, styled } from "@mui/material";
import { useNavigate } from "react-router-dom";

// STYLED COMPONENTS
const FlexBox = styled(Box)({
  display: "flex",
  alignItems: "center"
});

const JustifyBox = styled(FlexBox)({
  maxWidth: 320,
  flexDirection: "column",
  justifyContent: "center"
});

const IMG = styled("img")({
  width: "150%",
  marginBottom: "32px"
});

const NoDataRoot = styled(FlexBox)({
  width: "100%",
  alignItems: "center",
  justifyContent: "center",
  height: "100vh !important"
});

export default function NoData() {
  const navigate = useNavigate();

  return (
    <NoDataRoot>
      <JustifyBox>
        <IMG src="assets/images/No data-amico.svg" alt="" />

        <Button
          color="primary"
          variant="contained"
          sx={{ textTransform: "capitalize" }}
          onClick={() => navigate('/databaseSetup/captureimages')}> {/* Navigate to the dashboard */}
          Go Back
        </Button>
      </JustifyBox>
    </NoDataRoot>
  );
}
