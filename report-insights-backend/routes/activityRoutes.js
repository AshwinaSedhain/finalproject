import express from "express";
import prisma from "../lib/prisma.js";
import { authenticateUser } from "../middleware/authMiddleware.js"; // <-- new import

const router = express.Router();


// Protect all routes below this line
router.use(authenticateUser);

// Get all activities of the logged-in user
router.get("/", async (req, res) => {
  try {
    const userEmail = req.user.email;

    const user = await prisma.user.findUnique({
      where: { email: userEmail },
      include: { activities: true },
    });

    if (!user) {
      return res.status(404).json({ error: "User not found in database" });
    }

    res.json(user.activities);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to fetch activities" });
  }
});

// Create a new activity for the logged-in user
router.post("/", async (req, res) => {
  try {
    const { prompt, output } = req.body;
    const userEmail = req.user.email;

    const user = await prisma.user.findUnique({
      where: { email: userEmail },
    });

    if (!user) {
      return res.status(404).json({ error: "User not found in database" });
    }

    const activity = await prisma.activity.create({
      data: {
        userId: user.id,
        prompt,
        output: output || null,
      },
    });

    res.status(201).json(activity);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to create activity" });
  }
});

export default router;
