import express from "express";
import kernelRoute from "../kernel/v1/route";

const app = express();
app.use(express.json());
app.use("/", kernelRoute);

export default app;
