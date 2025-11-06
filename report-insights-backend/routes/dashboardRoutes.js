// routes/dashboardRoutes.js
import express from "express";
import axios from "axios";
import { authenticateUser } from "../middleware/authMiddleware.js";

const router = express.Router();

// Dashboard data endpoint
router.get('/data', authenticateUser, async (req, res) => {
  try {
    const { connection_string } = req.query;
    console.log(`[Backend] Fetching dashboard data for user ${req.user.id}...`);
    const DASHBOARD_SERVICE_URL = 'http://localhost:8000/dashboard/analytics';
    
    const params = {};
    if (connection_string) {
      params.connection_string = connection_string;
    }
    
    const aiServiceResponse = await axios.get(DASHBOARD_SERVICE_URL, { params });
    
    res.status(200).json(aiServiceResponse.data);
  } catch (error) {
    const errorMessage = error.response ? error.response.data.detail : error.message;
    console.error('[Backend] Error fetching dashboard data:', errorMessage);
    res.status(500).json({ error: 'Failed to get dashboard data from AI service.', details: errorMessage });
  }
});

export default router;


