import { Edit, Delete } from "@mui/icons-material";
import {
  Box,
  Card,
  Table,
  Select,
  Avatar,
  styled,
  TableRow,
  useTheme,
  MenuItem,
  TableBody,
  TableCell,
  TableHead,
  TableRow as MUITableRow,

  IconButton,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import Visibility from '@mui/icons-material/Visibility'; // For Material-UI icons

import { Paragraph } from "app/components/Typography";
import { useEffect, useState } from "react";
import axios from "axios";
import TrainingProgressModal from "./ProgressBar"; // Import the modal

// STYLED COMPONENTS
const CardHeader = styled(Box)(() => ({
  display: "flex",
  paddingLeft: "24px",
  paddingRight: "24px",
  marginBottom: "12px",
  alignItems: "center",
  justifyContent: "space-between",
}));

const Title = styled("span")(() => ({
  fontSize: "1rem",
  fontWeight: "500",
  textTransform: "capitalize",
}));

const ProductTable = styled(Table)(() => ({
  minWidth: 400,
  whiteSpace: "pre",
  "& small": {
    width: 50,
    height: 15,
    borderRadius: 500,
    boxShadow: "0 0 2px 0 rgba(0, 0, 0, 0.12), 0 2px 2px 0 rgba(0, 0, 0, 0.24)",
  },
  "& td": { borderBottom: "none", textAlign: "center" }, // Center-align data cells
  "& th": { borderBottom: "none", textAlign: "center" }, // Center-align header cells
  "& td:first-of-type": { paddingLeft: "16px !important" },
}));

const Small = styled("small")(({ bgcolor }) => ({
  width: 50,
  height: 15,
  color: "#fff",
  padding: "2px 8px",
  borderRadius: "4px",
  overflow: "hidden",
  background: bgcolor,
  boxShadow: "0 0 2px 0 rgba(0, 0, 0, 0.12), 0 2px 2px 0 rgba(0, 0, 0, 0.24)",
}));

const TrainButton = styled(Button)(({ theme }) => ({
  textTransform: "none",
  fontSize: "0.875rem",
  marginLeft: theme.spacing(2),
}));

const ActionButton = styled(IconButton)(() => ({
  margin: "0 2px",
}));

export default function DataTable() {
  const { palette } = useTheme();
  const bgError = palette.error.main;
  const bgPrimary = palette.primary.main;

  const [datasets, setDatasets] = useState([]);
  const [trainingInProgress, setTrainingInProgress] = useState(null);
  const [progress, setProgress] = useState(0);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentPieceLabel, setCurrentPieceLabel] = useState("");
  const [selectedDatasets, setSelectedDatasets] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  const [confirmationOpen, setConfirmationOpen] = useState(false);
  const [actionType, setActionType] = useState(""); // For storing the action type

  useEffect(() => {
    // Fetch data from the backend
    axios.get("http://localhost:8000/piece/datasets")
      .then((response) => {
        setDatasets(Object.values(response.data)); // Convert object to an array
      })
      .catch((error) => {
        console.error("Error fetching datasets:", error);
      });
  }, []);

  const handleTrain = (pieceLabel) => {
    setTrainingInProgress(pieceLabel);
    setCurrentPieceLabel(pieceLabel);
    setModalOpen(true);

    axios.post(`http://localhost:8000/detection/train/${pieceLabel}`)
      .then((response) => {
        // Simulate progress update
        const interval = setInterval(() => {
          setProgress((prevProgress) => {
            if (prevProgress === 100) {
              clearInterval(interval);
              setTrainingInProgress(null);
              setProgress(0);
              setModalOpen(false); // Close modal when training is complete
              return 100;
            }
            return Math.min(prevProgress + 10, 100);
          });
        }, 1000);
      })
      .catch((error) => {
        console.error("Error starting training:", error);
        setTrainingInProgress(null);
        setProgress(0);
        setModalOpen(false); // Close modal on error
      });
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setActionType("close");
      setConfirmationOpen(true);
    } else {
      setActionType("delete");
      setConfirmationOpen(true);
    }
  };

  const handleSelect = (label) => {
    setSelectedDatasets(prevSelected => 
      prevSelected.includes(label) 
        ? prevSelected.filter(item => item !== label) 
        : [...prevSelected, label]
    );
  };

  const handleView = (label) => {
    // Implement edit logic
    console.log("handleView", label);
  };


  const handleDelete = (label) => {
    // Implement delete logic
    axios.delete(`http://localhost:8000/piece/delete_piece/${label}`)
      .then(() => {
        // Refresh the datasets after deletion
        setDatasets(prevDatasets => prevDatasets.filter(dataset => dataset.label !== label));
        setSelectedDatasets(prevSelected => prevSelected.filter(item => item !== label));
  
        // Reload the window to reflect changes
        window.location.reload();
      })
      .catch((error) => {
        console.error("Error deleting piece:", error);
      });
  };
  
  const handleConfirmationClose = (confirm) => {
    setConfirmationOpen(false);
    if (confirm) {
      if (actionType === "delete") {
        // Call delete all API if selectAll was checked
        if (selectAll) {
          handleDeleteAll();
        } else {
          // Delete selected items
          selectedDatasets.forEach(label => handleDelete(label));
        }
      } else if (actionType === "close") {
        // Close the dialog and do nothing
      }
      setSelectAll(false); // Reset select all state
    }
  };
  //handle all kind delete 


  
  const handleDeleteAll = () => {
    axios.delete("http://localhost:8000/piece/delete_all_pieces")
      .then(() => {
        // Refresh the datasets after deletion
        setDatasets([]);
        setSelectedDatasets([]);
      })
      .catch((error) => {
        console.error("Error deleting all pieces:", error);
      });
  };


  // Group datasets by their common identifier
  const groupedDatasets = datasets.reduce((groups, dataset) => {
    const groupLabel = dataset.label.split(".").slice(0, 2).join(".");
    if (!groups[groupLabel]) {
      groups[groupLabel] = { label: groupLabel, pieces: [] };
    }
    groups[groupLabel].pieces.push(dataset);
    return groups;
  }, {});

  return (
    <>
      <Card elevation={3} sx={{ pt: "20px", mb: 3 }}>
        <CardHeader>
          <Title>Dataset Table</Title>
          <Select size="small" defaultValue="this_month">
            <MenuItem value="this_month">This Month</MenuItem>
            <MenuItem value="last_month">Last Month</MenuItem>
          </Select>
        </CardHeader>

        <Box overflow="auto">
          {Object.values(groupedDatasets).map((group, index) => (
            <Box key={index} mb={3}>
              <CardHeader>
                <Title>{group.label}</Title>
                {/* <TrainButton 
                  onClick={() => handleTrain(group.label)} 
                  variant="contained" 
                  color="primary"
                  disabled={trainingInProgress === group.label}
                >
                  {trainingInProgress === group.label ? "Training..." : "Train"}
                </TrainButton> */}
                <Button 
                  variant="outlined"
                  onClick={handleSelectAll}
                >
                  {selectAll ? "Deselect All" : "Select All"}
                </Button>
              </CardHeader>
              <ProductTable>
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox" align="center">
                      {/* Empty cell for select/deselect all button */}
                    </TableCell>
                    <TableCell colSpan={4} align="center">Name</TableCell>
                    <TableCell colSpan={2} align="center">Number of Images</TableCell>
                    <TableCell colSpan={2} align="center">Annotation Status</TableCell>
                    <TableCell colSpan={2} align="center">YOLO Training Status</TableCell>
                    <TableCell colSpan={2} align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>

                <TableBody>
                  {group.pieces.map((piece) => (
                    <TableRow key={piece.id} hover>
                      <TableCell colSpan={5} align="center">
                        <Box display="flex" alignItems="center" gap={4} justifyContent="center">
                          <Avatar src={piece.images[0]?.url} /> {/* Display the first image of the dataset */}
                          <Paragraph>{piece.label}</Paragraph>
                        </Box>
                      </TableCell>
                      <TableCell align="center" colSpan={2}>{piece.images.length}</TableCell>
                      <TableCell align="center" colSpan={2}>
                        {piece.is_annotated ? <Small bgcolor={bgPrimary}>Completed</Small> : <Small bgcolor={bgError}>Pending</Small>}
                      </TableCell>
                      <TableCell align="center" colSpan={2}>
                        {piece.is_yolo_trained ? <Small bgcolor={bgPrimary}>Trained</Small> : <Small bgcolor={bgError}>Not Trained</Small>}
                      </TableCell>
                      <TableCell align="center" colSpan={2}>
                        <ActionButton color="info" onClick={() => handleView(piece.label)}>
                          <Visibility /> {/* Use Visibility icon instead of Edit */}
                        </ActionButton>
                        <ActionButton color="error" onClick={() => handleDelete(piece.label)}>
                          <Delete />
                        </ActionButton>
                        <TrainButton 
                          onClick={() => handleTrain(piece.label)} 
                          variant="contained" 
                          color="primary"
                          disabled={trainingInProgress === piece.label}
                          sx={{ marginLeft: 2 }}
                        >
                          {trainingInProgress === piece.label ? "Training..." : "Train"}
                        </TrainButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>

              </ProductTable>
            </Box>
          ))}
        </Box>
      </Card>
      <TrainingProgressModal 
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        progress={progress}
      />

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmationOpen}
        onClose={() => setConfirmationOpen(false)}
      >
        <DialogTitle>
          {actionType === "delete" ? "Delete Selected Items" : "Close Selection"}
        </DialogTitle>
        <DialogContent>
          {actionType === "delete" 
            ? "Are you sure you want to delete the selected items?" 
            : "Are you sure you want to close the selection?"}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleConfirmationClose(false)}>Cancel</Button>
          <Button onClick={() => handleConfirmationClose(true)} color="primary">
            {actionType === "delete" ? "Delete" : "Close"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
