// File: backend/index.js

import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { Pool } from "pg"; // Import the pg Pool
import prisma from "./lib/prisma.js"; // Use the shared Prisma client

// Route imports
import userRoutes from "./routes/userRoutes.js";
import activityRoutes from "./routes/activityRoutes.js";
import authRoutes from "./routes/authRoutes.js";
import chatRoutes from "./routes/chatRoutes.js";

dotenv.config();
const app = express();

// Define the allowed origin (your frontend URL)
const corsOptions = {
  origin: 'http://localhost:5173', // Your React app's address
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));
app.use(express.json());

// API Routes
app.use("/api/users", userRoutes);
app.use("/api/activities", activityRoutes);
app.use("/api/auth", authRoutes);
app.use("/api/chat", chatRoutes);

// --- Root and TestDB endpoints for basic checks ---
app.get("/", (req, res) => {
  res.send("Backend is running 🚀");
});

app.get("/testdb-prisma", async (req, res) => {
  try {
    // This tests the connection configured in your .env's DATABASE_URL
    const userCount = await prisma.user.count();
    res.json({ status: "success", message: `Prisma connected successfully. Found ${userCount} users.` });
  } catch (e) {
    res.status(500).json({ status: "error", message: `Prisma failed to connect: ${e.message}` });
  }
});


// --- THIS IS THE NEW, CRITICAL ROUTE HANDLER ---
app.post("/api/db/test-connection", async (req, res) => {
  const { connectionString } = req.body;

  if (!connectionString) {
    return res.status(400).json({ status: 'error', message: 'connectionString is required.' });
  }

  const pool = new Pool({ connectionString });
  
  try {
    // Try to get a client from the pool. This is the actual connection test.
    const client = await pool.connect();
    // If it succeeds, release the client back to the pool.
    client.release();
    // Send a success response back to the frontend.
    res.status(200).json({ status: 'success', message: 'Connection successful!' });
  } catch (error) {
    console.error("Database connection test failed:", error.message);
    res.status(500).json({ status: 'error', message: `Connection failed. Please check your connection string.` });
  } finally {
    // Always close the pool to prevent hanging connections.
    await pool.end();
  }
});


// --- Start the server ---
const PORT = process.env.PORT || 5000;
app.listen(PORT, () =>
  console.log(`✅ Backend server running on port ${PORT}`)
);