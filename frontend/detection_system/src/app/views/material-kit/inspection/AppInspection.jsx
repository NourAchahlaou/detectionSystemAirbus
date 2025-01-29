import React, { useState, useEffect } from "react";
import { Stack, Box, styled, Button, TextField, Select, MenuItem, Snackbar, SnackbarContent } from "@mui/material";
import { Breadcrumb } from "app/components";
import "./AppInspection.css";
import axios from 'axios';
const styles = {
  container: {
    padding: '20px',
    maxWidth: '600px',
    margin: '0 auto',
    fontFamily: 'Arial, sans-serif',
  },
  title: {
    textAlign: 'center',
    marginBottom: '20px',
  },
  profile: {
    border: '1px solid #ddd',
    padding: '15px',
    borderRadius: '5px',
    backgroundColor: '#f9f9f9',
  },
  error: {
    color: 'red',
    textAlign: 'center',
    marginTop: '20px',
  },
  loading: {
    textAlign: 'center',
    fontSize: '18px',
  },
};

// STYLED COMPONENTS
const Container = styled("div")(({ theme }) => ({
  margin: "30px",
  [theme.breakpoints.down("sm")]: { margin: "16px" },
  "& .breadcrumb": {
    marginBottom: "30px",
    [theme.breakpoints.down("sm")]: { marginBottom: "16px" }
  }
}));

const VideoFeed = ({ cameraId, targetLabel, freeze }) => {
  const [videoUrl, setVideoUrl] = useState('');

  useEffect(() => {
    if (cameraId && targetLabel && !freeze) {
      setVideoUrl(`http://127.0.0.1:8000/detection/video_feed?camera_id=${cameraId}&target_label=${targetLabel}`);
    }
  }, [cameraId, targetLabel, freeze]);

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', position: 'relative' }}>
      <img
        src={videoUrl}
        style={{ width: '1100px', maxHeight: '650px', filter: freeze ? 'grayscale(100%)' : 'none' }}
        alt="Video Feed"
      />
      {freeze && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '10px',
          borderRadius: '5px',
        }}>
          Image Saved!
        </div>
      )}
    </div>
  );
};

export default function AppInspection() {
  const [targetLabel, setTargetLabel] = useState('');
  const [cameraId, setCameraId] = useState('');
  const [isCameraStarted, setIsCameraStarted] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [selectedCameraId, setSelectedCameraId] = useState('');
  const [OF, setOF] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [freeze, setFreeze] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Retrieve the token from local storage
  const token = localStorage.getItem('token');

  // Move this useEffect before the conditional returns
  useEffect(() => {
    if (!token) {
      setError('No authentication token found.');
      setLoading(false);
      return;
    }

    // Fetch user profile from the backend
    axios
      .get('http://127.0.0.1:8000/users/profile', {
        headers: {
          Authorization: `Bearer ${token}`, // Include token in headers
        },
      })
      .then((response) => {
        setUserProfile(response.data);
        setLoading(false);
      })
      .catch((err) => {
        const errorMessage = err.response?.data?.detail || 'Failed to load profile data.';
        setError(errorMessage);
        setLoading(false);
      });
  }, [token]);

  useEffect(() => {
    const fetchData = async () => {
        try {
            // Load the model
            const modelResponse = await axios.get("http://127.0.0.1:8000/detection/load_model");
            console.log(modelResponse.data.message); // Model loaded successfully

            // Fetch camera data
            const cameraResponse = await axios.get("http://127.0.0.1:8000/cameras/get_allcameras/");
            setCameras(cameraResponse.data);
        } catch (err) {
            console.error("Error occurred:", err);
            setError("Failed to load data.");
        } finally {
            setLoading(false); // Set loading to false after both calls
        }
    };

    fetchData(); // Call the async function
}, []);

  if (loading) return <p style={styles.loading}>Loading...</p>;
  if (error) return <p style={styles.error}>{error}</p>;

  const handleCameraChange = (event) => {
    const selectedCameraId = event.target.value;
    setSelectedCameraId(selectedCameraId);
    setCameraId(selectedCameraId);
  };

  const handleStartCamera = () => {
    if (cameraId && targetLabel && OF) {
      setIsCameraStarted(true);
    } else {
      alert("Please enter a valid camera ID, order of fabrication, and target label.");
    }
  };

  const stopCameraFeed = async () => {
    try {
      await axios.post('http://127.0.0.1:8000/detection/stop_camera_feed/');
      await fetch("http://127.0.0.1:8000/cameras/cleanup-temp-photos", {
        method: "POST",
      });
      setIsCameraStarted(false);
    } catch (error) {
      console.error('There was an error stopping the camera feed!', error);
    }
  };

  const captureImage = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/detection/capture_image?camera_id=${cameraId}&of=${OF}&target_label=${targetLabel}&user_id=${userProfile.user_id}`);
      if (response.status === 200) {
        setFreeze(true); // Freeze video feed
        setSnackbarMessage("Image captured and saved successfully!");
        setSnackbarOpen(true);
        setTimeout(() => {
          setFreeze(false); // Unfreeze after 2 seconds
        }, 2000);
      }
    } catch (error) {
      console.error('There was an error capturing the image!', error);
      setSnackbarMessage("Error capturing image.");
      setSnackbarOpen(true);
    }
  };

  const handleStopCamera = () => {
    stopCameraFeed();
    window.location.reload(); // Reload the page
  };
  

  const handleTargetLabelChange = (event) => {
    setTargetLabel(event.target.value);
  };

  const handleOFChange = (event) => {
    setOF(event.target.value);
  };

  const handleCaptureImage = () => {
    captureImage();
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Container>
      <Box className="breadcrumb">
        <Breadcrumb routeSegments={[{ name: "Inspection" }]} />
      </Box>
      <Stack spacing={3}>
        <div className="controls" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ flexDirection: 'column', display: 'flex', alignItems: 'left' }}>
            <TextField
              label="Target Label"
              value={targetLabel}
              onChange={handleTargetLabelChange}
              style={{ marginBottom: '10px' }}
            />
            <TextField
              label="Ordre de Fabrication (OF)"
              value={OF}
              onChange={handleOFChange}
            />
          </div>
          <Select
            labelId="camera-select-label"
            value={selectedCameraId}
            onChange={handleCameraChange}
            displayEmpty
          >
            <MenuItem value="" disabled>Select a Camera</MenuItem>
            {cameras.map((camera) => (
              <MenuItem key={camera.camera_id} value={camera.camera_id}>
                {camera.model}
              </MenuItem>
            ))}
          </Select>
        </div>
        {isCameraStarted ? (
          <VideoFeed cameraId={cameraId} targetLabel={targetLabel} freeze={freeze} />
        ) : (
          <p style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>No Video Feed</p>
        )}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Button
            variant="contained"
            onClick={handleStartCamera}
            disabled={isCameraStarted || !cameraId || !targetLabel}
            style={{ margin: '10px' }}
          >
            Start Camera
          </Button>
          <div style={{ display: 'flex', alignItems: 'center', opacity: isCameraStarted ? 1 : 0 }}>
            <Button
              variant="contained"
              onClick={handleStopCamera}
              disabled={!isCameraStarted}
              style={{ margin: '10px' }}
            >
              Stop Camera
            </Button>
            <Button
              variant="contained"
              onClick={handleCaptureImage}
              disabled={!isCameraStarted}
              style={{ margin: '10px' }}
            >
              Capture Image
            </Button>
          </div>
        </div>
      </Stack>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
      >
        <SnackbarContent
          style={{
            backgroundColor: snackbarMessage.includes("Error") ? "red" : "green",
          }}
          message={snackbarMessage}
        />
      </Snackbar>
    </Container>
  );
}
