// routes/authRoutes.js
import express from "express";
import { supabase } from "../supabaseClient.js";
import prisma from "../lib/prisma.js";
const router = express.Router();


// Sign up
router.post("/signup", async (req, res) => {
  const { email, password, name } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: "Email and password required" });
  }

  try {
    // Create user in Supabase auth
    const { data, error } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true, // auto confirm email
    });

    if (error) return res.status(400).json({ error: error.message });

    // Create user in Prisma database
    const user = await prisma.user.create({
      data: {
        email,
        name: name || null,
      },
    });

    res.status(201).json({ user, supabaseId: data.id });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Signup failed" });
  }
});

// Sign in
router.post("/signin", async (req, res) => {
  const { email, password } = req.body;

  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) return res.status(400).json({ error: error.message });

    res.status(200).json({ user: data.user, session: data.session });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Signin failed" });
  }
});

export default router;
