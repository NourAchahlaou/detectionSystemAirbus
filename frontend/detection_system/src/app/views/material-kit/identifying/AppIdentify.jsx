import React, { useState, useEffect } from "react";
import { Stack, Box, styled, Button, TextField, Select, MenuItem } from "@mui/material";
import { Breadcrumb } from "app/components";
import "./AppIdentify.css";
import axios from 'axios';

// STYLED COMPONENTS
const Container = styled("div")(({ theme }) => ({
  margin: "30px",
  [theme.breakpoints.down("sm")]: { margin: "16px" },
  "& .breadcrumb": {
    marginBottom: "30px",
    [theme.breakpoints.down("sm")]: { marginBottom: "16px" }
  }
}));

const VideoFeed = ({ cameraId }) => {
  const [videoUrl, setVideoUrl] = useState('');

  useEffect(() => {
    if (cameraId) {
      setVideoUrl(`http://127.0.0.1:8000/identify/video_identify_feed?camera_id=${cameraId}`);
    }
  }, [cameraId]);

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <img
        src={videoUrl}
        style={{ width: '1100px', maxHeight: '650px' }}
        alt="Video Feed"
      />
    </div>
  );
};

export default function AppIdentify() {
  const [cameraId, setCameraId] = useState(''); // Camera ID state
  const [isCameraStarted, setIsCameraStarted] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [selectedCameraId, setSelectedCameraId] = useState('');

  useEffect(() => {
    // Fetch the list of cameras from the backend
    axios.get('http://127.0.0.1:8000/cameras/get_allcameras/')
      .then(response => {
        setCameras(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the camera data!', error);
      });
  }, []);

  const handleCameraChange = (event) => {
    const selectedCameraId = event.target.value;
    setSelectedCameraId(selectedCameraId);
    setCameraId(selectedCameraId); // Update cameraId state when a camera is selected
  };


  const handleStartCamera = () => {
    if (cameraId) {
      setIsCameraStarted(true);
    } else {
      alert("Please enter a valid camera ID and target label.");
    }
  };

  const stopCameraFeed = async () => {
    try {
      await axios.post('http://127.0.0.1:8000/identify/stop_camera_identify_feed/');
      await fetch("http://127.0.0.1:8000/cameras/cleanup-temp-photos", {
        method: "POST",
      });
      setIsCameraStarted(false);
    } catch (error) {
      console.error('There was an error stopping the camera feed!', error);
    }
  };


  const handleStopCamera = () => {
    stopCameraFeed();
  };


  return (
    <Container>
      <Box className="breadcrumb">
        <Breadcrumb routeSegments={[{ name: "Identify" }]} />
      </Box>
      <Stack spacing={3}>
        <div className="controls">

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
          <VideoFeed cameraId={cameraId} />
        ) : (
          <p style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>No Video Feed</p>
        )}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Button
            variant="contained"
            onClick={handleStartCamera}
            disabled={isCameraStarted || !cameraId }
            style={{ margin: '10px' }}
          >
            Start Camera
          </Button>
          <Button
            variant="contained"
            onClick={handleStopCamera}
            disabled={!isCameraStarted}
            style={{ margin: '10px' }}
          >
            Stop Camera
          </Button>
        </div>
      </Stack>
    </Container>
  );
}
