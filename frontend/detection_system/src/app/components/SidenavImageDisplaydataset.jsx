import { useEffect, useState } from "react";
import { Box, Card, styled } from "@mui/material";
import Scrollbar from "react-perfect-scrollbar";
import BadgeSelected from "./MatxCustomizer/BadgeSelected";

const MaxCustomaizer = styled("div")(({ theme }) => ({
  width: "auto",
  right: "10px",
  display: "flex",
  height: "75vh",
  paddingBottom: "32px",
  flexDirection: "column",
 
}));

const LayoutBox = styled(BadgeSelected)(() => ({
  width: "100%",
  height: "100px !important",
  cursor: "pointer",
  marginTop: "12px",
  marginBottom: "12px",
  
  "& .layout-name": { display: "none" },
  "&:hover .layout-name": {
    width: "100%",
    height: "100%",
    display: "flex",
    alignItems: "center",
    position: "absolute",
    justifyContent: "center",
  },
}));

const IMG = styled("img")(() => ({ width: "100%" }));

const StyledScrollBar = styled(Scrollbar)(() => ({
  paddingLeft: "16px",
  paddingRight: "16px",
}));

export default function SidenavImageDisplay({ pieceLabel, onImageSelect, onFirstImageLoad }) { 
  const [images, setImages] = useState([]);

  useEffect(() => {
    async function fetchImages() {
      if (!pieceLabel) return; // Do nothing if no pieceLabel is provided

      try {
        const response = await fetch(`http://127.0.0.1:8000/piece/get_images_of_piece/${pieceLabel}`);
        if (!response.ok) {
          throw new Error("Failed to fetch images");
        }
        const data = await response.json();
        setImages(data); 
        console.log("data that was fetched ",data )

        if (data.length > 0 && onFirstImageLoad) {
          onFirstImageLoad(data[0].url); // Automatically select the first image if available
        }
      } catch (error) {
        console.error("Error fetching images:", error);
      }
    }

    fetchImages();
  }, [pieceLabel]); // Refetch images when pieceLabel changes

  return (
    <MaxCustomaizer>
      <StyledScrollBar>
        <div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            {images.map((image, index) => (
              <LayoutBox key={index} onClick={() => onImageSelect(image.url)}>
                <Card elevation={4} sx={{ position: "relative"}}>
                  <IMG src={image.url} alt={`Image ${index}`} />
                </Card>
              </LayoutBox>
            ))}
          </div>
        </div>
      </StyledScrollBar>
    </MaxCustomaizer>
  );
}
