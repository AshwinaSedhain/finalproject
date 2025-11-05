// File: backend/index.js

import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { Pool } from "pg";
import prisma from "./lib/prisma.js";

import userRoutes from "./routes/userRoutes.js";
import activityRoutes from "./routes/activityRoutes.js";
import authRoutes from "./routes/authRoutes.js";
import chatRoutes from "./routes/chatRoutes.js";

dotenv.config();
const app = express();

const corsOptions = {
  origin: 'http://localhost:5173',
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));
app.use(express.json());

app.use("/api/users", userRoutes);
app.use("/api/activities", activityRoutes);
app.use("/api/auth", authRoutes);
app.use("/api/chat", chatRoutes);

app.get("/", (req, res) => res.send("Backend is running 🚀"));

app.post("/api/db/test-connection", async (req, res) => {
  const { connectionString } = req.body;
  if (!connectionString) {
    return res.status(400).json({ status: 'error', message: 'connectionString is required.' });
  }
  const pool = new Pool({ connectionString });
  try {
    const client = await pool.connect();
    client.release();
    res.status(200).json({ status: 'success', message: 'Connection successful!' });
  } catch (error) {
    console.error("Database connection test failed:", error.message);
    res.status(500).json({ status: 'error', message: `Connection failed. Please check your connection string.` });
  } finally {
    await pool.end();
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`✅ Backend server running on port ${PORT}`));