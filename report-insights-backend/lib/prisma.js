// File: backend/lib/prisma.js

import { PrismaClient } from '@prisma/client';

// This creates one single, shared instance of Prisma for your whole app
const prisma = new PrismaClient();

export default prisma;