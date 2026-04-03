import express from "express";
import { handleKernelRequest } from "./handler";

const router = express.Router();

router.post("/kernel/v1/route", async (req, res) => {
  const result = await handleKernelRequest(req.body);

  if (!result.success) {
    return res.status(400).json(result);
  }

  res.json(result);
});

export default router;
