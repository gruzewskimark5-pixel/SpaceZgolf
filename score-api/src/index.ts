import express from 'express';
import cors from 'cors';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
import crypto from 'crypto';
import { UserRepo } from './repos/userRepo';
import { SessionRepo } from './repos/sessionRepo';
import { ScoreRepo } from './repos/scoreRepo';
import { ReplayRepo } from './repos/replayRepo';
import { requireAuth, optionalAuth, AuthRequest } from './middleware/auth';
import rateLimit from 'express-rate-limit';

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors());

// Security: Add basic security headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  next();
});

if (!process.env.JWT_SECRET || !process.env.JWT_REFRESH_SECRET) {
  throw new Error('JWT_SECRET and JWT_REFRESH_SECRET must be defined in environment variables');
}
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_REFRESH_SECRET = process.env.JWT_REFRESH_SECRET;

function hashRefreshToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex');
}

// GET /health
app.get('/health', (req, res) => {
  res.json({ status: 'ok', version: '1.0.0' });
});

// POST /simulateShot
app.post('/simulateShot', (req, res) => {
  // Mock physics preview
  res.json({ success: true, preview: 'simulation_data_here' });
});

// Security: Rate limiting for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per `window` (here, per 15 minutes)
  message: { error: 'Too many authentication attempts, please try again after 15 minutes' },
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
});

// POST /auth/register
app.post('/auth/register', authLimiter, async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      res.status(400).json({ error: 'Missing required fields' });
      return;
    }

    const passwordHash = await bcrypt.hash(password, 12);
    const user = await UserRepo.createUser(username, email, passwordHash);

    const accessToken = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '15m' });
    const refreshToken = jwt.sign({ userId: user.id }, JWT_REFRESH_SECRET, { expiresIn: '7d' });
    const refreshTokenHash = hashRefreshToken(refreshToken);

    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7);

    await SessionRepo.createSession(user.id, refreshTokenHash, expiresAt);

    res.json({ accessToken, refreshToken });
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /auth/login
app.post('/auth/login', authLimiter, async (req, res) => {
  try {
    const { identifier, password } = req.body;
    if (!identifier || !password) {
       res.status(400).json({ error: 'Missing identifier or password' });
       return;
    }

    const user = await UserRepo.findByUsernameOrEmail(identifier);
    if (!user) {
      res.status(401).json({ error: 'Invalid credentials' });
      return;
    }

    const valid = await bcrypt.compare(password, user.passwordHash);
    if (!valid) {
      res.status(401).json({ error: 'Invalid credentials' });
      return;
    }

    const accessToken = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '15m' });
    const refreshToken = jwt.sign({ userId: user.id }, JWT_REFRESH_SECRET, { expiresIn: '7d' });
    const refreshTokenHash = hashRefreshToken(refreshToken);

    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7);

    await SessionRepo.createSession(user.id, refreshTokenHash, expiresAt);

    res.json({ accessToken, refreshToken });
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /auth/refresh
app.post('/auth/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;
    if (!refreshToken) {
       res.status(400).json({ error: 'Missing refresh token' });
       return;
    }

    let payload;
    try {
      payload = jwt.verify(refreshToken, JWT_REFRESH_SECRET) as { userId: number };
    } catch (err) {
      res.status(401).json({ error: 'Invalid token' });
      return;
    }

    const user = await UserRepo.findById(payload.userId);
    if (!user) {
      res.status(401).json({ error: 'Invalid user' });
      return;
    }

    const refreshTokenHash = hashRefreshToken(refreshToken);
    const session = await SessionRepo.findSession(user.id, refreshTokenHash);
    if (!session) {
       // Stolen token reuse triggers full session purge for the user.
       await SessionRepo.revokeAllSessionsForUser(user.id);
       res.status(401).json({ error: 'Session compromised. All sessions revoked.' });
       return;
    }

    // Revoke the specific old session
    await SessionRepo.revokeSession(session.id);

    const newAccessToken = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '15m' });
    const newRefreshToken = jwt.sign({ userId: user.id }, JWT_REFRESH_SECRET, { expiresIn: '7d' });
    const newRefreshTokenHash = hashRefreshToken(newRefreshToken);

    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7);

    await SessionRepo.createSession(user.id, newRefreshTokenHash, expiresAt);

    res.json({ accessToken: newAccessToken, refreshToken: newRefreshToken });
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /auth/logout
app.post('/auth/logout', requireAuth, async (req: AuthRequest, res) => {
  try {
    const userId = req.user!.userId;
    const authHeader = req.headers.authorization;
    if (authHeader) {
      // Typically the client would also send the refresh token to revoke just that session,
      // but revoking all is safe for logout if we don't know the exact session.
      // A better implementation would take the refresh token in the body and revoke only that one.
      const { refreshToken } = req.body;
      if (refreshToken) {
         const refreshTokenHash = hashRefreshToken(refreshToken);
         const session = await SessionRepo.findSession(userId, refreshTokenHash);
         if (session) {
           await SessionRepo.revokeSession(session.id);
           res.json({ success: true });
           return;
         }
      }
    }
    await SessionRepo.revokeAllSessionsForUser(userId);
    res.json({ success: true });
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /leaderboard/:courseId
app.get('/leaderboard/:courseId', optionalAuth, async (req: AuthRequest, res) => {
  try {
    const { courseId } = req.params;
    const leaderboard = await ScoreRepo.getLeaderboard(courseId);

    const response: any = { leaderboard };
    if (req.user) {
      response.userBest = await ScoreRepo.getUserBest(req.user.userId, courseId);
    }

    res.json(response);
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /submitScore
app.post('/submitScore', requireAuth, async (req: AuthRequest, res) => {
  try {
    const userId = req.user!.userId;
    const { courseId, score, replayData, seasonId } = req.body;

    if (!courseId || score === undefined || !replayData) {
      res.status(400).json({ error: 'Missing required fields' });
      return;
    }

    const newScore = await ScoreRepo.submitScoreWithReplay(userId, courseId, score, replayData, seasonId);
    res.json(newScore);
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /validateReplay
app.post('/validateReplay', requireAuth, async (req: AuthRequest, res) => {
  try {
    const { scoreId, isValid } = req.body;
    if (!scoreId || isValid === undefined) {
      res.status(400).json({ error: 'Missing required fields' });
      return;
    }

    const replay = await ReplayRepo.findByScoreId(scoreId);
    if (!replay) {
      res.status(404).json({ error: 'Replay not found' });
      return;
    }

    const verifiedStatus = isValid ? 1 : -1;
    await ReplayRepo.setVerifiedStatus(replay.id, verifiedStatus);

    res.json({ success: true, verified: verifiedStatus });
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /me/scores
app.get('/me/scores', requireAuth, async (req: AuthRequest, res) => {
  try {
    const userId = req.user!.userId;
    const scores = await ScoreRepo.getUserScores(userId);
    res.json(scores);
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
