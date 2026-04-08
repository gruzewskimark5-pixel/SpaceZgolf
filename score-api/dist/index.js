"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const bcrypt_1 = __importDefault(require("bcrypt"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const dotenv_1 = __importDefault(require("dotenv"));
const crypto_1 = __importDefault(require("crypto"));
const userRepo_1 = require("./repos/userRepo");
const sessionRepo_1 = require("./repos/sessionRepo");
const scoreRepo_1 = require("./repos/scoreRepo");
const replayRepo_1 = require("./repos/replayRepo");
const auth_1 = require("./middleware/auth");
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
dotenv_1.default.config();
const app = (0, express_1.default)();
app.use(express_1.default.json());
app.use((0, cors_1.default)());
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
function hashRefreshToken(token) {
    return crypto_1.default.createHash('sha256').update(token).digest('hex');
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
const authLimiter = (0, express_rate_limit_1.default)({
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
        const passwordHash = await bcrypt_1.default.hash(password, 12);
        const user = await userRepo_1.UserRepo.createUser(username, email, passwordHash);
        const accessToken = jsonwebtoken_1.default.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '15m' });
        const refreshToken = jsonwebtoken_1.default.sign({ userId: user.id }, JWT_REFRESH_SECRET, { expiresIn: '7d' });
        const refreshTokenHash = hashRefreshToken(refreshToken);
        const expiresAt = new Date();
        expiresAt.setDate(expiresAt.getDate() + 7);
        await sessionRepo_1.SessionRepo.createSession(user.id, refreshTokenHash, expiresAt);
        res.json({ accessToken, refreshToken });
    }
    catch (err) {
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
        const user = await userRepo_1.UserRepo.findByUsernameOrEmail(identifier);
        if (!user) {
            res.status(401).json({ error: 'Invalid credentials' });
            return;
        }
        const valid = await bcrypt_1.default.compare(password, user.passwordHash);
        if (!valid) {
            res.status(401).json({ error: 'Invalid credentials' });
            return;
        }
        const accessToken = jsonwebtoken_1.default.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '15m' });
        const refreshToken = jsonwebtoken_1.default.sign({ userId: user.id }, JWT_REFRESH_SECRET, { expiresIn: '7d' });
        const refreshTokenHash = hashRefreshToken(refreshToken);
        const expiresAt = new Date();
        expiresAt.setDate(expiresAt.getDate() + 7);
        await sessionRepo_1.SessionRepo.createSession(user.id, refreshTokenHash, expiresAt);
        res.json({ accessToken, refreshToken });
    }
    catch (err) {
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
            payload = jsonwebtoken_1.default.verify(refreshToken, JWT_REFRESH_SECRET);
        }
        catch (err) {
            res.status(401).json({ error: 'Invalid token' });
            return;
        }
        const user = await userRepo_1.UserRepo.findById(payload.userId);
        if (!user) {
            res.status(401).json({ error: 'Invalid user' });
            return;
        }
        const refreshTokenHash = hashRefreshToken(refreshToken);
        const session = await sessionRepo_1.SessionRepo.findSession(user.id, refreshTokenHash);
        if (!session) {
            // Stolen token reuse triggers full session purge for the user.
            await sessionRepo_1.SessionRepo.revokeAllSessionsForUser(user.id);
            res.status(401).json({ error: 'Session compromised. All sessions revoked.' });
            return;
        }
        // Revoke the specific old session
        await sessionRepo_1.SessionRepo.revokeSession(session.id);
        const newAccessToken = jsonwebtoken_1.default.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '15m' });
        const newRefreshToken = jsonwebtoken_1.default.sign({ userId: user.id }, JWT_REFRESH_SECRET, { expiresIn: '7d' });
        const newRefreshTokenHash = hashRefreshToken(newRefreshToken);
        const expiresAt = new Date();
        expiresAt.setDate(expiresAt.getDate() + 7);
        await sessionRepo_1.SessionRepo.createSession(user.id, newRefreshTokenHash, expiresAt);
        res.json({ accessToken: newAccessToken, refreshToken: newRefreshToken });
    }
    catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// POST /auth/logout
app.post('/auth/logout', auth_1.requireAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const authHeader = req.headers.authorization;
        if (authHeader) {
            // Typically the client would also send the refresh token to revoke just that session,
            // but revoking all is safe for logout if we don't know the exact session.
            // A better implementation would take the refresh token in the body and revoke only that one.
            const { refreshToken } = req.body;
            if (refreshToken) {
                const refreshTokenHash = hashRefreshToken(refreshToken);
                const session = await sessionRepo_1.SessionRepo.findSession(userId, refreshTokenHash);
                if (session) {
                    await sessionRepo_1.SessionRepo.revokeSession(session.id);
                    res.json({ success: true });
                    return;
                }
            }
        }
        await sessionRepo_1.SessionRepo.revokeAllSessionsForUser(userId);
        res.json({ success: true });
    }
    catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// GET /leaderboard/:courseId
app.get('/leaderboard/:courseId', auth_1.optionalAuth, async (req, res) => {
    try {
        const { courseId } = req.params;
        const leaderboard = await scoreRepo_1.ScoreRepo.getLeaderboard(courseId);
        const response = { leaderboard };
        if (req.user) {
            response.userBest = await scoreRepo_1.ScoreRepo.getUserBest(req.user.userId, courseId);
        }
        res.json(response);
    }
    catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// POST /submitScore
app.post('/submitScore', auth_1.requireAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const { courseId, score, replayData, seasonId } = req.body;
        if (!courseId || score === undefined || !replayData) {
            res.status(400).json({ error: 'Missing required fields' });
            return;
        }
        const newScore = await scoreRepo_1.ScoreRepo.submitScoreWithReplay(userId, courseId, score, replayData, seasonId);
        res.json(newScore);
    }
    catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// POST /validateReplay
app.post('/validateReplay', auth_1.requireAuth, async (req, res) => {
    try {
        const { scoreId, isValid } = req.body;
        if (!scoreId || isValid === undefined) {
            res.status(400).json({ error: 'Missing required fields' });
            return;
        }
        const replay = await replayRepo_1.ReplayRepo.findByScoreId(scoreId);
        if (!replay) {
            res.status(404).json({ error: 'Replay not found' });
            return;
        }
        const verifiedStatus = isValid ? 1 : -1;
        await replayRepo_1.ReplayRepo.setVerifiedStatus(replay.id, verifiedStatus);
        res.json({ success: true, verified: verifiedStatus });
    }
    catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal server error' });
    }
});
// GET /me/scores
app.get('/me/scores', auth_1.requireAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const scores = await scoreRepo_1.ScoreRepo.getUserScores(userId);
        res.json(scores);
    }
    catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal server error' });
    }
});
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
