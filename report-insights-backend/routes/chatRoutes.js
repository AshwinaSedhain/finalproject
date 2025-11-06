// report-insights-backend/routes/chatRoutes.js
import express from "express";
import axios from "axios";
import { authenticateUser } from "../middleware/authMiddleware.js";

const router = express.Router();

// --- Main Chat Query Route ---
router.post('/query', authenticateUser, async (req, res) => {
  try {
    const { user_prompt, connection_string } = req.body;
    const user_id = req.user.id; 

    if (!user_prompt || !user_id) {
      return res.status(400).json({ error: 'user_prompt and a valid user session are required.' });
    }

    console.log(`[Backend] Proxying chat request for user ${user_id} to AI service...`);
    const AI_SERVICE_URL = 'http://localhost:8000/process-query';
    const requestBody = { user_prompt, user_id };
    if (connection_string) {
      requestBody.connection_string = connection_string;
    }
    
    // Add timeout to prevent hanging (60 seconds)
    const aiServiceResponse = await axios.post(AI_SERVICE_URL, requestBody, {
      timeout: 60000  // 60 second timeout
    });

    res.status(200).json(aiServiceResponse.data);
  } catch (error) {
    const errorMessage = error.response ? (error.response.data.detail || error.response.data.error || JSON.stringify(error.response.data)) : error.message;
    console.error('[Backend] Error proxying chat query:', errorMessage);
    console.error('[Backend] Full error:', error);
    // If the AI service returned an error response, pass it through
    if (error.response && error.response.data && error.response.data.response) {
      return res.status(200).json(error.response.data);
    }
    res.status(500).json({ error: 'An error occurred with the AI service.', details: errorMessage });
  }
});

// 👇 --- NEW ROUTE ADDED HERE --- 👇
router.get('/database-summary', authenticateUser, async (req, res) => {
    try {
        console.log(`[Backend] Proxying request for DB summary to AI service...`);
        const SUMMARY_SERVICE_URL = 'http://localhost:8000/database-summary';
        
        const aiServiceResponse = await axios.get(SUMMARY_SERVICE_URL);

        res.status(200).json(aiServiceResponse.data);
    } catch (error) {
        const errorMessage = error.response ? error.response.data.detail : error.message;
        console.error('[Backend] Error proxying for DB summary:', errorMessage);
        res.status(500).json({ error: 'Failed to get database summary from AI service.', details: errorMessage });
    }
});

// Clear old database connections endpoint
router.post('/database/clear-old', authenticateUser, async (req, res) => {
  try {
    const { old_connection_string } = req.body;
    console.log(`[Backend] Clearing old database connection...`);
    const CLEAR_SERVICE_URL = 'http://localhost:8000/clear-old-connections';
    
    const response = await axios.post(CLEAR_SERVICE_URL, {
      old_connection_string: old_connection_string || null
    });
    
    res.status(200).json(response.data);
  } catch (error) {
    const errorMessage = error.response ? error.response.data.detail : error.message;
    console.error('[Backend] Error clearing old connection:', errorMessage);
    // Don't fail the request - this is cleanup
    res.status(200).json({ success: false, error: errorMessage });
  }
});

export default router;