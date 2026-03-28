import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FB_API_KEY || "dummy",
  authDomain: process.env.NEXT_PUBLIC_FB_AUTH_DOMAIN || "dummy",
  projectId: process.env.NEXT_PUBLIC_FB_PROJECT_ID || "dummy",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
