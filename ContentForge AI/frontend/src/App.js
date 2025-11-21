import React, { useState, useEffect } from 'react';
import {
  Container,
  TextField,
  Button,
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Paper,
  CircularProgress,
  Card,
  CardMedia,
  CardContent,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  ThemeProvider,
  createTheme,
  useMediaQuery,
  Skeleton,
  Fade,
  Zoom,
  Stack,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
} from '@mui/icons-material';
import axios from 'axios';
import {
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';

// API configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Main App component for LinkedIn Content Generator
 * Handles user input, API calls, and displays generated content
 */
function App() {
  // State management
  const [prompt, setPrompt] = useState('');
  const [enableWebSearch, setEnableWebSearch] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

  /**
   * Handle form submission and content generation
   */
  // Add new state variables
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [toneStyle, setToneStyle] = useState('professional');
  const [operation, setOperation] = useState('generate');
  const [templates, setTemplates] = useState({});

  // Add template fields state
  const [templateFields, setTemplateFields] = useState({});

  useEffect(() => {
    // Fetch templates when component mounts
    const fetchTemplates = async () => {
      try {
        const response = await axios.get(`${API_URL}/templates`);
        setTemplates(response.data);
      } catch (err) {
        setError('Failed to load templates');
      }
    };
    
    fetchTemplates();
  }, []);

  // Modify handleSubmit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setCopySuccess(false);

    try {
      const response = await axios.post(`${API_URL}/generate`, {
        prompt: selectedTemplate ? 
          templates[selectedTemplate].template.replace(
            /{(\w+)}/g, 
            (_, key) => templateFields[key] || '{' + key + '}'
          ) : prompt,
        web_search: enableWebSearch,
        tone_style: toneStyle,
        operation: operation,
        ...(selectedTemplate && { template_id: selectedTemplate })
      });
      setResult(response.data);
    } catch (err) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || 'An error occurred while generating content');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle copying generated text to clipboard
   */
  const handleCopyText = async () => {
    if (!result?.text) return;
    
    try {
      await navigator.clipboard.writeText(result.text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      setError('Failed to copy text to clipboard');
    }
  };

  /**
   * Handle downloading generated image
   */
  const handleDownloadImage = async () => {
    if (!result?.image_url) return;
    
    try {
      const response = await fetch(result.image_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'linkedin-content-image.png';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to download image');
    }
  };

  const [darkMode, setDarkMode] = useState(false);
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [isLoading, setIsLoading] = useState(true);

  // Create theme based on dark mode
  const theme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? 'dark' : 'light',
          primary: {
            main: darkMode ? '#1e88e5' : '#0a66c2',
          },
          secondary: {
            main: darkMode ? '#66bb6a' : '#057642',
          },
          background: {
            default: darkMode ? '#121212' : '#f5f5f5',
            paper: darkMode ? '#1e1e1e' : '#ffffff',
          },
        },
        typography: {
          fontFamily: '"Segoe UI", "Roboto", "Arial", sans-serif',
          h4: {
            fontWeight: 600,
          },
        },
        components: {
          MuiPaper: {
            styleOverrides: {
              root: {
                borderRadius: 12,
                transition: 'all 0.3s ease-in-out',
              },
            },
          },
          MuiButton: {
            styleOverrides: {
              root: {
                borderRadius: 8,
                textTransform: 'none',
                transition: 'all 0.3s ease-in-out',
              },
            },
          },
        },
      }),
    [darkMode]
  );

  useEffect(() => {
    setDarkMode(prefersDarkMode);
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, [prefersDarkMode]);

  // Loading skeleton component
  const LoadingSkeleton = () => (
    <Stack spacing={2}>
      <Skeleton variant="rectangular" height={60} />
      <Skeleton variant="rectangular" height={200} />
      <Skeleton variant="rectangular" height={60} />
    </Stack>
  );

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          minHeight: '100vh',
          bgcolor: 'background.default',
          transition: 'all 0.3s ease-in-out',
        }}
      >
        <AppBar position="sticky" elevation={0}>
          <Toolbar sx={{ flexDirection: { xs: 'column', sm: 'row' }, py: { xs: 1, sm: 0 } }}>
            <Box sx={{ flexGrow: 1, textAlign: { xs: 'center', sm: 'left' } }}>
              <Typography variant="h5" component="div" sx={{ fontWeight: 600 }}>
                ContentForge AI
              </Typography>
              <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>
                LinkedIn Content Generator
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: { xs: 1, sm: 0 } }}>
              <Typography variant="caption" sx={{ mr: 2, opacity: 0.7 }}>
                Created by Mayuresh Khot
              </Typography>
              <IconButton
                color="inherit"
                onClick={() => setDarkMode(!darkMode)}
                sx={{ ml: 1 }}
              >
                {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>

        <Container maxWidth="md" sx={{ py: { xs: 2, md: 4 } }}>
          <Fade in={!isLoading} timeout={1000}>
            <Box>
              {isLoading ? (
                <LoadingSkeleton />
              ) : (
                <Zoom in={!isLoading} timeout={500}>
                  <Paper
                    elevation={darkMode ? 2 : 3}
                    sx={{
                      p: { xs: 2, md: 4 },
                      mb: 4,
                      backdropFilter: 'blur(10px)',
                      backgroundColor: darkMode
                        ? 'rgba(30, 30, 30, 0.9)'
                        : 'rgba(255, 255, 255, 0.9)',
                    }}
                  >
                    <form onSubmit={handleSubmit}>
                      <Grid container spacing={3}>
                        <Grid item xs={12}>
                          <FormControl fullWidth>
                            <InputLabel>Select Template</InputLabel>
                            <Select
                              value={selectedTemplate}
                              onChange={(e) => setSelectedTemplate(e.target.value)}
                              disabled={loading}
                            >
                              <MenuItem value="">Custom Prompt</MenuItem>
                              {Object.entries(templates).map(([id, template]) => (
                                <MenuItem key={id} value={id}>
                                  {template.name}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        </Grid>

                        {/* Add Dynamic Template Fields */}
                        {selectedTemplate && templates[selectedTemplate]?.template && (
                          <Grid item xs={12}>
                            {Array.from(
                              templates[selectedTemplate].template.matchAll(/{(\w+)}/g)
                            ).map(([_, key]) => (
                              <TextField
                                key={key}
                                fullWidth
                                label={key.charAt(0).toUpperCase() + key.slice(1)}
                                value={templateFields[key] || ''}
                                onChange={(e) => setTemplateFields(prev => ({
                                  ...prev,
                                  [key]: e.target.value
                                }))}
                                sx={{ mb: 2 }}
                                disabled={loading}
                              />
                            ))}
                          </Grid>
                        )}

                        {/* Show prompt field only if no template is selected */}
                        {!selectedTemplate && (
                          <Grid item xs={12}>
                            <TextField
                              fullWidth
                              multiline
                              rows={4}
                              label="Enter your prompt"
                              value={prompt}
                              onChange={(e) => setPrompt(e.target.value)}
                              disabled={loading}
                              placeholder="What would you like to generate?"
                            />
                          </Grid>
                        )}

                        <Grid item xs={12}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={enableWebSearch}
                                onChange={(e) => setEnableWebSearch(e.target.checked)}
                                disabled={loading}
                              />
                            }
                            label="Enable Web Search"
                          />
                        </Grid>

                        <Grid item xs={12}>
                          
                          <Button
                            type="submit"
                            variant="contained"
                            fullWidth
                            disabled={loading || (selectedTemplate ? Object.keys(templateFields).length === 0 : !prompt)}
                            startIcon={loading ? <CircularProgress size={20} /> : null}
                          >
                            {loading ? 'Generating...' : 'Generate Content'}
                          </Button>
                        </Grid>
                      </Grid>
                    </form>
                  </Paper>
                </Zoom>
              )}

              {/* Results Display with animations */}
              {result && (
                <Fade in={true} timeout={1000}>
                  <Paper
                    elevation={darkMode ? 2 : 3}
                    sx={{
                      p: { xs: 2, md: 4 },
                      mt: 4,
                      backgroundColor: darkMode
                        ? 'rgba(30, 30, 30, 0.9)'
                        : 'rgba(255, 255, 255, 0.9)',
                    }}
                  >
                    {result.text && (
                      <Card sx={{ mb: 3 }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                            <Typography variant="h6">
                              Generated Text
                            </Typography>
                            <Tooltip title="Copy to clipboard">
                              <IconButton onClick={handleCopyText} color={copySuccess ? "success" : "default"}>
                                <CopyIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                          <Divider sx={{ mb: 2 }} />
                          <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                            {result.text}
                          </Typography>
                        </CardContent>
                      </Card>
                    )}

                    {/* Rest of the result display components */}
                  </Paper>
                </Fade>
              )}
            </Box>
          </Fade>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;