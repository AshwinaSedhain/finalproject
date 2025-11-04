// report-insights-backend/routes/chatRoutes.js
import express from "express";
import axios from "axios";
import { authenticateUser } from "../middleware/authMiddleware.js";

const router = express.Router();

// --- Main Chat Query Route ---
router.post('/query', authenticateUser, async (req, res) => {
  try {
    const { user_prompt } = req.body;
    const user_id = req.user.id; 

    if (!user_prompt || !user_id) {
      return res.status(400).json({ error: 'user_prompt and a valid user session are required.' });
    }

    console.log(`[Backend] Proxying chat request for user ${user_id} to AI service...`);
    const AI_SERVICE_URL = 'http://localhost:8000/process-query';
    const aiServiceResponse = await axios.post(AI_SERVICE_URL, { user_prompt, user_id });

    res.status(200).json(aiServiceResponse.data);
  } catch (error) {
    const errorMessage = error.response ? error.response.data.detail : error.message;
    console.error('[Backend] Error proxying chat query:', errorMessage);
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

export default router;