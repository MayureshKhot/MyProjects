import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import InvoiceManagement from './components/InvoiceManagement';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <InvoiceManagement />
    </ThemeProvider>
  );
}

export default App;
