import { Box, styled } from "@mui/material";
import { Breadcrumb } from "app/components";
import DataTable from "./DataTable"; // Import the DataTable component
import NoData from "../../sessions/NoData"; // Import the NoData component
import { useState, useEffect } from "react";
import axios from "axios"; // Import axios or any other data-fetching library
import { useNavigate } from "react-router-dom"; // Import useNavigate

// STYLED COMPONENTS
const Container = styled("div")(({ theme }) => ({
  margin: "30px",
  [theme.breakpoints.down("sm")]: { margin: "16px" },
  "& .breadcrumb": {
    marginBottom: "30px",
    [theme.breakpoints.down("sm")]: { marginBottom: "16px" }
  }
}));

export default function AppDatabasesetup() {
  const [data, setData] = useState(null); // State to manage data
  const [loading, setLoading] = useState(true); // State to manage loading state
  const [error, setError] = useState(null); // State to manage errors
  const navigate = useNavigate(); // Initialize navigate

  useEffect(() => {
    // Fetch data from the API
    const fetchData = async () => {
      setLoading(true); // Set loading to true before fetching data
      try {
        const response = await axios.get("http://localhost:8000/piece/datasets");
        const pieces = response.data;
        setData(pieces); // Set data if fetch is successful

        // Handle cases where pieces are empty
        if (!pieces || Object.keys(pieces).length === 0) {
          navigate("/204"); // Redirect to No Data page if no pieces are found
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to fetch data"); // Set error state if fetch fails
        navigate("/204"); // Redirect to No Data page on error
      } finally {
        setLoading(false); // Set loading to false after fetch is complete
      }
    };

    fetchData();
  }, [navigate]);

  if (loading) return <div>Loading...</div>; // Optionally handle loading state
  if (error) return <div>{error}</div>; // Optionally handle error state

  return (
    <Container>
      <Box className="breadcrumb">
        <Breadcrumb routeSegments={[{ name: "Database Setup" }]} />
      </Box>

      {data && Object.keys(data).length > 0 ? (
        <DataTable data={data} /> // Pass data to DataTable component if needed
      ) : (
        <NoData />
      )}
    </Container>
  );
}
