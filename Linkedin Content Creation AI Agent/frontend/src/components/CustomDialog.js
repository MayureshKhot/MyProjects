import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
} from '@mui/material';

export default function CustomDialog({ open, type, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    [type === 'template' ? 'template' : 'modifier']: '',
  });

  const handleSubmit = () => {
    onSubmit(formData);
    setFormData({ name: '', description: '', template: '', modifier: '' });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Create Custom {type === 'template' ? 'Template' : 'Tone'}
      </DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          margin="normal"
        />
        <TextField
          fullWidth
          label="Description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          margin="normal"
        />
        <TextField
          fullWidth
          multiline
          rows={4}
          label={type === 'template' ? 'Template Pattern' : 'Tone Modifier'}
          value={formData[type === 'template' ? 'template' : 'modifier']}
          onChange={(e) =>
            setFormData({
              ...formData,
              [type === 'template' ? 'template' : 'modifier']: e.target.value,
            })
          }
          margin="normal"
          helperText={
            type === 'template'
              ? 'Use {variable} for dynamic fields'
              : 'Describe the tone style and characteristics'
          }
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">
          Create
        </Button>
      </DialogActions>
    </Dialog>
  );
}