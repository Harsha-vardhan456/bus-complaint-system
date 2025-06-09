import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  MenuItem,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { PhotoCamera } from '@mui/icons-material';
import axios from 'axios';

const categories = [
  'Bus Delays',
  'Overcrowding',
  'Route Issues',
  'Accessibility Problems',
  'Bus Cleanliness',
  'Lost Items',
  'Suggestions for Improvement',
];

const ComplaintForm = () => {
  const [formData, setFormData] = useState({
    busNumber: '',
    routeNumber: '',
    complaintType: '',
    description: '',
    location: '',
    date: new Date().toISOString().split('T')[0],
    image: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
      if (!validTypes.includes(file.type)) {
        setError('Please upload a valid image file (JPG, PNG, or GIF)');
        return;
      }
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image size should be less than 5MB');
        return;
      }

      setFormData({ ...formData, image: file });
      setImagePreview(URL.createObjectURL(file));
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('busNumber', formData.busNumber);
      formDataToSend.append('routeNumber', formData.routeNumber);
      formDataToSend.append('complaintType', formData.complaintType);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('location', formData.location);
      formDataToSend.append('date', formData.date);
      if (formData.image) {
        formDataToSend.append('image', formData.image);
      }

      const response = await axios.post(
        `${import.meta.env.VITE_APP_API_URL}/api/complaints`,
        formDataToSend,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      setSuccess(true);
      setFormData({
        busNumber: '',
        routeNumber: '',
        complaintType: '',
        description: '',
        location: '',
        date: new Date().toISOString().split('T')[0],
        image: null
      });
      setImagePreview(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to submit complaint');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Submit a Complaint
      </Typography>

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Complaint submitted successfully!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit} noValidate>
        <TextField
          required
          fullWidth
          label="Bus Number"
          name="busNumber"
          value={formData.busNumber}
          onChange={handleInputChange}
          margin="normal"
        />

        <TextField
          required
          fullWidth
          label="Route Number"
          name="routeNumber"
          value={formData.routeNumber}
          onChange={handleInputChange}
          margin="normal"
        />

        <TextField
          required
          fullWidth
          select
          label="Complaint Type"
          name="complaintType"
          value={formData.complaintType}
          onChange={handleInputChange}
          margin="normal"
        >
          {categories.map((category) => (
            <MenuItem key={category} value={category}>
              {category}
            </MenuItem>
          ))}
        </TextField>

        <TextField
          required
          fullWidth
          label="Location"
          name="location"
          value={formData.location}
          onChange={handleInputChange}
          margin="normal"
        />

        <TextField
          required
          fullWidth
          type="date"
          label="Date of Incident"
          name="date"
          value={formData.date}
          onChange={handleInputChange}
          margin="normal"
          InputLabelProps={{ shrink: true }}
        />

        <TextField
          required
          fullWidth
          multiline
          rows={4}
          label="Description"
          name="description"
          value={formData.description}
          onChange={handleInputChange}
          margin="normal"
        />

        <Box sx={{ mt: 2, mb: 2 }}>
          <input
            accept="image/*"
            style={{ display: 'none' }}
            id="image-upload"
            type="file"
            onChange={handleImageChange}
          />
          <label htmlFor="image-upload">
            <Button
              variant="outlined"
              component="span"
              startIcon={<PhotoCamera />}
            >
              Upload Image
            </Button>
          </label>

          {imagePreview && (
            <Box sx={{ mt: 2 }}>
              <img
                src={imagePreview}
                alt="Preview"
                style={{ maxWidth: '100%', maxHeight: '200px' }}
              />
            </Box>
          )}
        </Box>

        <Button
          type="submit"
          fullWidth
          variant="contained"
          disabled={loading}
          sx={{ mt: 2 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Submit Complaint'}
        </Button>
      </Box>
    </Paper>
  );
};

export default ComplaintForm;