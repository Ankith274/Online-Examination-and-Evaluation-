import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box, Paper, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TablePagination,
  Chip, Button, TextField, MenuItem, Select, FormControl,
  InputLabel, DatePicker, Grid, Card, CardContent, Alert,
  IconButton, Menu, Dialog, DialogTitle, DialogContent
} from '@mui/material';
import {
  PictureAsPdf, TableChart, FileDownload, FilterList,
  Search, DateRange, Print, FileExcel, Visibility
} from '@mui/icons-material';
import jsPDF from 'jspdf'; // npm i jspdf jspdf-autotable
import 'jspdf-autotable';
import Papa from 'papaparse'; // npm i papaparse
import { Pie, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale,
  LinearScale, BarElement, Title
} from 'chart.js';
import axios from 'axios';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const Reports = ({ examId, role = 'admin' }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [filters, setFilters] = useState({
    search: '',
    status: 'all',
    dateFrom: null,
    dateTo: null,
    scoreMin: '',
    scoreMax: ''
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState('pdf');

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  // Mock comprehensive exam data
  const mockData = useMemo(() => Array.from({ length: 200 }, (_, i) => ({
    id: `STU${String(i + 1).padStart(4, '0')}`,
    name: `Student ${i + 1}`,
    email: `student${i + 1}@exam.ac.in`,
    score: Math.floor(Math.random() * 90) + 10,
    total: 100,
    percentage: ((Math.random() * 90) + 10).toFixed(1),
    status: Math.random() > 0.1 ? 'Passed' : 'Failed',
    startTime: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toLocaleString(),
    duration: `${Math.floor(Math.random() * 120) + 30}m`,
    violations: Math.floor(Math.random() * 5),
    proctorScore: Math.floor(Math.random() * 100),
    institute: ['IIT Hyderabad', 'NIT Warangal', 'JNTU'][Math.floor(i / 67)]
  })), []);

  // Charts data
  const chartData = useMemo(() => {
    const passed = data.filter(row => row.status === 'Passed').length;
    const failed = data.length - passed;
    
    return {
      pie: {
        labels: ['Passed', 'Failed'],
        datasets: [{
          data: [passed, failed],
          backgroundColor: ['#48bb78', '#f56565']
        }]
      },
      bar: {
        labels: data.map(row => row.id.slice(0, 8)),
        datasets: [{
          label: 'Score %',
          data: data.map(row => parseFloat(row.percentage)),
          backgroundColor: data.map(row => row.status === 'Passed' ? '#48bb78' : '#f56565')
        }]
      }
    };
  }, [data]);

  // Filter data
  const filteredData = useMemo(() => {
    return mockData.filter(row => {
      const matchesSearch = row.name.toLowerCase().includes(filters.search.toLowerCase()) ||
                           row.id.toLowerCase().includes(filters.search.toLowerCase()) ||
                           row.email.toLowerCase().includes(filters.search.toLowerCase());
      
      const matchesStatus = filters.status === 'all' || row.status === filters.status;
      const matchesScore = (!filters.scoreMin || parseFloat(row.percentage) >= parseFloat(filters.scoreMin)) &&
                          (!filters.scoreMax || parseFloat(row.percentage) <= parseFloat(filters.scoreMax));
      
      const matchesDate = (!filters.dateFrom || new Date(row.startTime) >= filters.dateFrom) &&
                         (!filters.dateTo || new Date(row.startTime) <= filters.dateTo);
      
      return matchesSearch && matchesStatus && matchesScore && matchesDate;
    });
  }, [mockData, filters]);

  // Load data
  useEffect(() => {
    const fetchReports = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_BASE}/reports/${examId || 'all'}`, {
          params: filters
        });
        setData(res.data);
      } catch (err) {
        console.error('Reports fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [examId, filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(0);
  };

  // Export functions
  const exportPDF = useCallback(() => {
    const doc = new jsPDF('l', 'mm', 'a4'); // Landscape
    const tableData = filteredData.map(row => [
      row.id, row.name, row.email, row.percentage, row.status,
      row.violations, row.proctorScore, row.startTime
    ]);

    doc.setFontSize(20);
    doc.text('Exam Results Report', 20, 20);
    doc.setFontSize(12);
    doc.text(`Generated: ${new Date().toLocaleString()} | Records: ${filteredData.length}`, 20, 35);

    doc.autoTable({
      head: [['ID', 'Name', 'Email', '%', 'Status', 'Violations', 'Proctor %', 'Started']],
      body: tableData,
      startY: 50,
      styles: { fontSize: 9, cellPadding: 3 },
      headStyles: { fillColor: [33, 150, 243], textColor: 255, fontStyle: 'bold' },
      alternateRowStyles: { fillColor: [245, 245, 245] },
      margin: { top: 60 },
      didDrawPage: (data) => {
        // Footer
        const pageCount = doc.internal.getNumberOfPages();
        doc.setFontSize(10);
        doc.text(`Page ${data.pageNumber} of ${pageCount}`, 280, 290);
      }
    });

    // Summary chart (text-based)
    doc.setFontSize(14);
    doc.text('Summary:', 20, doc.lastAutoTable.finalY + 20);
    doc.text(`Total: ${filteredData.length} | Passed: ${filteredData.filter(r => r.status === 'Passed').length}`, 20, doc.lastAutoTable.finalY + 35);

    doc.save(`exam-report-${examId || 'all'}-${Date.now()}.pdf`);
    setExportDialogOpen(false);
  }, [filteredData, examId]);

  const exportCSV = useCallback(() => {
    const csv = Papa.unparse(filteredData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `exam-report-${examId || 'all'}-${Date.now()}.csv`;
    link.click();
    setExportDialogOpen(false);
  }, [filteredData, examId]);

  const exportExcel = useCallback(() => {
    // Simplified - use xlsx library for full Excel
    const csvContent = "data:text/csv;charset=utf-8," + 
      Papa.unparse(filteredData.map(row => ({
        ID: row.id, Name: row.name, Email: row.email,
        Score: `${row.percentage}%`, Status: row.status,
        Violations: row.violations
      })));
    const encodedUri = encodeURI(csvContent);
    window.open(encodedUri);
    setExportDialogOpen(false);
  }, [filteredData]);

  const handleExport = () => {
    switch (exportFormat) {
      case 'pdf': exportPDF(); break;
      case 'csv': exportCSV(); break;
      case 'excel': exportExcel(); break;
    }
  };

  const emptyState = !loading && filteredData.length === 0;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Exam Reports {examId && ` - ${examId}`}
          </Typography>
          <Typography variant="h6" color="text.secondary">
            {filteredData.length} results • Generated {new Date().toLocaleString()}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button 
            variant="outlined" 
            startIcon={<FileDownload />}
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            Export
          </Button>
          <Button variant="contained" startIcon={<FilterList />}>
            Advanced Filters
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              label="Search ID/Name"
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              InputProps={{ startAdornment: <Search /> }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status}
                label="Status"
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="Passed">Passed</MenuItem>
                <MenuItem value="Failed">Failed</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              label="Score Range"
              value={`${filters.scoreMin || ''}-${filters.scoreMax || ''}`}
              onChange={(e) => {
                const [min, max] = e.target.value.split('-');
                handleFilterChange('scoreMin', min || '');
                handleFilterChange('scoreMax', max || '');
              }}
              placeholder="0-100"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button fullWidth variant="outlined" startIcon={<DateRange />}>
              Date Range
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 350 }}>
            <Typography variant="h6" gutterBottom>Pass/Fail Distribution</Typography>
            <Box sx={{ height: 250 }}>
              <Pie data={chartData.pie} />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 350 }}>
            <Typography variant="h6" gutterBottom>Top Performers</Typography>
            <Box sx={{ height: 250 }}>
              <Bar data={chartData.bar} options={{ indexAxis: 'y' }} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Main Table */}
      <Paper sx={{ overflow: 'hidden' }}>
        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <LinearProgress sx={{ mb: 2 }} />
            <Typography>Loading reports...</Typography>
          </Box>
        ) : emptyState ? (
          <Box sx={{ p: 8, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              No results found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Try adjusting your filters
            </Typography>
          </Box>
        ) : (
          <>
            <TableContainer sx={{ maxHeight: 600 }}>
              <Table stickyHeader>
                <TableHead sx={{ bgcolor: 'primary.light' }}>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Score</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Violations</TableCell>
                    <TableCell>Proctor Score</TableCell>
                    <TableCell>Started</TableCell>
                    <TableCell sx={{ minWidth: 120 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredData
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((row) => (
                      <TableRow key={row.id} hover>
                        <TableCell><Chip label={row.id} size="small" /></TableCell>
                        <TableCell>{row.name}</TableCell>
                        <TableCell sx={{ fontSize: '0.875rem' }}>{row.email}</TableCell>
                        <TableCell>
                          <Chip 
                            label={`${row.percentage}%`} 
                            color={parseFloat(row.percentage) >= 60 ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={row.status} 
                            color={row.status === 'Passed' ? 'success' : 'error'}
                          />
                        </TableCell>
                        <TableCell sx={{ color: row.violations > 2 ? 'error.main' : 'warning.main' }}>
                          {row.violations}
                        </TableCell>
                        <TableCell>{row.proctorScore}%</TableCell>
                        <TableCell sx={{ fontSize: '0.875rem' }}>
                          {new Date(row.startTime).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <IconButton size="small"><Visibility /></IconButton>
                          <IconButton size="small" color="primary"><Print /></IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            <TablePagination
              rowsPerPageOptions={[10, 25, 50, 100]}
              component="div"
              count={filteredData.length}
              page={page}
              onPageChange={(e, p) => setPage(p)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value));
                setPage(0);
              }}
              labelRowsPerPage="Rows per page:"
              labelDisplayedRows={({ from, to, count }) => `${from}-${to} of ${count}`}
            />
          </>
        )}
      </Paper>

      {/* Export Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={() => { setExportFormat('pdf'); setExportDialogOpen(true); }}>
          <PictureAsPdf sx={{ mr: 1 }} /> PDF Report
        </MenuItem>
        <MenuItem onClick={() => { setExportFormat('csv'); setExportDialogOpen(true); }}>
          <FileDownload sx={{ mr: 1 }} /> CSV Data
        </MenuItem>
        <MenuItem onClick={() => { setExportFormat('excel'); setExportDialogOpen(true); }}>
          <FileExcel sx={{ mr: 1 }} /> Excel Export
        </MenuItem>
      </Menu>

      {/* Export Confirmation Dialog */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)}>
        <DialogTitle>Export {exportFormat.toUpperCase()} Report</DialogTitle>
        <DialogContent>
          <Typography>Export {filteredData.length} records?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleExport} variant="contained" startIcon={<FileDownload />}>
            Download {exportFormat.toUpperCase()}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Reports;
