import React, { useEffect, useState } from 'react';
import {
  Box, Container, Typography, Button, Paper, TextField,
  Chip, Alert, Fade, Grid, Link, CircularProgress
} from '@mui/material';
import {
  ErrorOutline, Search, School, Dashboard, Login,
  HelpOutline, MailOutline, Phone
} from '@mui/icons-material';
import { motion } from 'framer-motion'; // npm i framer-motion
import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [redirecting, setRedirecting] = useState(false);

  // Quick recovery links
  const quickLinks = [
    { label: 'Student Dashboard', icon: School, path: '/dashboard' },
    { label: 'Login', icon: Login, path: '/login' },
    { label: 'My Exams', icon: Assignment, path: '/exams' },
    { label: 'Admin Panel', icon: Dashboard, path: '/admin' }
  ];

  // Auto-redirect after 10s
  useEffect(() => {
    const timer = setTimeout(() => {
      setRedirecting(true);
      setTimeout(() => navigate('/dashboard'), 2000);
    }, 10000);

    return () => clearTimeout(timer);
  }, [navigate]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Search exams/users
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 6,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background Pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.1,
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='3'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      <Container maxWidth="md">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <Paper
            elevation={24}
            sx={{
              p: { xs: 4, md: 6 },
              borderRadius: 4,
              textAlign: 'center',
              position: 'relative',
              overflow: 'hidden',
              bgcolor: 'rgba(255,255,255,0.95)',
              backdropFilter: 'blur(20px)'
            }}
          >
            {/* Header */}
            <ErrorOutline 
              sx={{ 
                fontSize: 96, 
                color: 'error.main', 
                mb: 2,
                transform: 'rotate(-10deg)'
              }} 
            />
            
            <Typography 
              variant="h2" 
              component="h1" 
              gutterBottom 
              sx={{ fontWeight: 700, mb: 1 }}
            >
              404
            </Typography>
            
            <Typography 
              variant="h5" 
              gutterBottom 
              color="text.secondary"
              sx={{ mb: 4, maxWidth: 400, mx: 'auto' }}
            >
              Page Not Found
            </Typography>

            <Typography 
              variant="body1" 
              color="text.secondary" 
              sx={{ mb: 4, lineHeight: 1.6 }}
            >
              The exam page you're looking for doesn't exist or has been moved. 
              Try searching or use the quick links below.
            </Typography>

            {/* Search */}
            <Paper 
              component="form" 
              elevation={2}
              sx={{ 
                p: 2, 
                mb: 4, 
                borderRadius: 3,
                maxWidth: 500,
                mx: 'auto'
              }}
              onSubmit={handleSearch}
            >
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Search sx={{ color: 'text.secondary', mt: 0.5 }} />
                <TextField
                  fullWidth
                  placeholder="Search exams, students, or courses..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  variant="outlined"
                  size="small"
                />
              </Box>
            </Paper>

            {/* Quick Links */}
            <Box sx={{ mb: 4 }}>
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ color: 'text.primary', mb: 3 }}
              >
                Quick Recovery
              </Typography>
              
              <Grid container spacing={2} justifyContent="center">
                {quickLinks.map((link, index) => {
                  const Icon = link.icon;
                  return (
                    <Grid item key={link.label}>
                      <Button
                        variant="contained"
                        startIcon={<Icon />}
                        onClick={() => navigate(link.path)}
                        sx={{
                          borderRadius: 3,
                          px: 3,
                          minWidth: 140,
                          animationDelay: `${index * 100}ms`
                        }}
                      >
                        {link.label}
                      </Button>
                    </Grid>
                  );
                })}
              </Grid>
            </Box>

            {/* Support */}
            <Alert severity="info" sx={{ mb: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                <HelpOutline sx={{ mt: 0.5 }} />
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Need Help?
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 1 }}>
                    <Link href="mailto:support@examsys.com" underline="hover">
                      <MailOutline sx={{ mr: 0.5, verticalAlign: 'middle', fontSize: 18 }} />
                      support@examsys.com
                    </Link>
                    <Link href="tel:+914012345678" underline="hover">
                      <Phone sx={{ mr: 0.5, verticalAlign: 'middle', fontSize: 18 }} />
                      +91 40 1234 5678
                    </Link>
                  </Box>
                </Box>
              </Box>
            </Alert>

            {/* Auto-redirect */}
            {redirecting ? (
              <Fade in={true}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2">
                    Redirecting to Dashboard...
                  </Typography>
                </Box>
              </Fade>
            ) : (
              <Fade in={true}>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/dashboard')}
                  sx={{ borderRadius: 3, px: 4 }}
                >
                  Go to Dashboard
                </Button>
              </Fade>
            )}
          </Paper>
        </motion.div>
      </Container>
    </Box>
  );
};

export default NotFound;
