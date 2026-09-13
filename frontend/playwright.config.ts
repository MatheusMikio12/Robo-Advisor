import { defineConfig } from "@playwright/test";
import path from "node:path";

const backend = path.resolve("../backend");
const python = process.platform === "win32" ? `"${path.join(backend,".venv/Scripts/python.exe")}"` : "python";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  workers: 1,
  use: {baseURL:"http://127.0.0.1:8082", browserName:"chromium", trace:"retain-on-failure"},
  webServer: [
    {command:`${python} -m uvicorn app.main:app --host 127.0.0.1 --port 8002`,cwd:backend,url:"http://127.0.0.1:8002/",reuseExistingServer:false,
      env:{DEBUG:"True",SECRET_KEY:"e2e-only-not-a-production-key-123456",DATABASE_URL:"sqlite:///./prisma-e2e.db",CORS_ORIGINS:'["http://127.0.0.1:8082"]',LLM_PROVIDER:"deterministic",RATE_LIMIT_ENABLED:"False"}},
    {command:"npm run dev -- --host 127.0.0.1 --port 8082 --strictPort",url:"http://127.0.0.1:8082",reuseExistingServer:false,env:{VITE_API_URL:"http://127.0.0.1:8002"}},
  ],
});
