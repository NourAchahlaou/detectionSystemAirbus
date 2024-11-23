import { Edit, Delete, Visibility } from "@mui/icons-material";
import {
  Box,
  Select,
  MenuItem,
  Card,
  Table,
  TableRow,
  TableBody,
  TableCell,
  TableHead,
  styled,
  useTheme,
  Button,
  TablePagination,
} from "@mui/material";
import { useEffect, useState } from "react";
import axios from "axios";

// STYLED COMPONENTS
const CardHeader = styled(Box)(() => ({
  display: "flex",
  padding: "16px 24px",
  marginBottom: "12px",
  alignItems: "center",
  justifyContent: "space-between",
  backgroundColor: "#f5f5f5",
  borderRadius: "8px",
  boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
}));

const Title = styled("span")(() => ({
  fontSize: "1.25rem",
  fontWeight: "600",
  color: "#333",
}));

const ProductTable = styled(Table)(() => ({
  minWidth: 400,
  whiteSpace: "pre",
  borderCollapse: "collapse",
  "& td, & th": { 
    borderBottom: "1px solid #ddd", 
    textAlign: "center", 
    padding: "12px",
  },
  "& th": {
    backgroundColor: "#f0f0f0",
    fontWeight: "bold",
    color: "#555",
  },
}));

const ActionButton = styled(Button)(({ theme }) => ({
  margin: "0 2px",
  padding: "6px 12px",
  borderRadius: "5px",
  textTransform: "none",
  "&:hover": {
    filter: "brightness(0.9)",
  },
}));

const FilterSelect = styled(Select)(() => ({
  marginLeft: "16px",
  backgroundColor: "#fff",
  borderRadius: "5px",
  "& .MuiSelect-select": {
    padding: "10px",
  },
}));

export default function DataTable({ user_id }) {
  const theme = useTheme();
  const [sessions, setSessions] = useState([]);
  const [filteredSessions, setFilteredSessions] = useState([]);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [page, setPage] = useState(0);
  const [filter, setFilter] = useState("today"); // Filter value

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/users/users/${user_id}/sessions`)
      .then((response) => {
        setSessions(response.data); // Set session data
        filterSessions(response.data, "today"); // Apply initial filter
      })
      .catch((error) => {
        console.error("Error fetching user sessions:", error);
      });
  }, [user_id]);

  // Group and combine all sessions into one array with dates
  const combineSessionsWithDate = (sessions) => {
    return sessions.map((session) => {
      const loginDate = new Date(session.login_time);
      return {
        date: loginDate.toLocaleDateString(),
        login_time: loginDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        logout_time: session.logout_time
          ? new Date(session.logout_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          : "Active",
      };
    });
  };

  // Handle the filter selection
  const handleFilterChange = (event) => {
    const selectedFilter = event.target.value;
    setFilter(selectedFilter);
    filterSessions(sessions, selectedFilter);
    setPage(0); // Reset to first page when filter changes
  };

  // Apply filter to sessions based on the selected time range
  const filterSessions = (allSessions, filter) => {
    const now = new Date();
    let filtered = allSessions;

    if (filter === "today") {
      filtered = allSessions.filter(session => new Date(session.login_time).toLocaleDateString() === now.toLocaleDateString());
    } else if (filter === "this_week") {
      const startOfWeek = new Date();
      startOfWeek.setDate(now.getDate() - now.getDay());
      filtered = allSessions.filter(session => new Date(session.login_time) >= startOfWeek);
    } else if (filter === "this_month") {
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      filtered = allSessions.filter(session => new Date(session.login_time) >= startOfMonth);
    }

    setFilteredSessions(combineSessionsWithDate(filtered));
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Render sessions with date shown only for the first session of each day
  const renderSessions = () => {
    let lastDate = null;
    return filteredSessions
      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
      .map((session, index) => {
        const showDate = session.date !== lastDate; // Show date only if it's a new day
        lastDate = session.date;
        return (
          <TableRow key={index}>
            <TableCell>{showDate ? session.date : ""}</TableCell>
            <TableCell>{session.login_time}</TableCell>
            <TableCell>{session.logout_time}</TableCell>
          </TableRow>
        );
      });
  };

  return (
    <Card elevation={3} sx={{ pt: "20px", mb: 3 }}>
      <CardHeader>
        <Title>Session Logs</Title>
        <FilterSelect size="small" value={filter} onChange={handleFilterChange}>
          <MenuItem value="today">Today</MenuItem>
          <MenuItem value="this_week">This Week</MenuItem>
          <MenuItem value="this_month">This Month</MenuItem>
          <MenuItem value="all_time">All Time</MenuItem>
        </FilterSelect>
      </CardHeader>

      <Box overflow="auto">
        <ProductTable>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Login Time</TableCell>
              <TableCell>Logout Time</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>{renderSessions()}</TableBody>
        </ProductTable>
      </Box>

      <TablePagination
        rowsPerPageOptions={[5, 10, 15]}
        component="div"
        count={filteredSessions.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Card>
  );
}
