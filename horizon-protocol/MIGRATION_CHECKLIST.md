# Migration Checklist: AI Studio → Sovereign Environment

## Phase 1: Extraction
- [ ] **Extract Viewer Code**: Download the viewer bundle from AI Studio (or rebuild it locally using React/Svelte). Place inside `viewer/` folder.
- [ ] **Extract Kernel Logic**: Move your Python kernel code out of AI Studio notebooks. Map them to FastAPI endpoints inside `kernel/main.py`.
- [ ] **Extract Doctrine**: Export your current doctrine and state machine configurations into JSON/YAML files and place them in `data/doctrine/`.

## Phase 2: Local Verification
- [ ] **Build Containers**: Run `docker-compose build` from the root directory.
- [ ] **Start Sovereign Stack**: Run `docker-compose up -d`.
- [ ] **Verify Kernel**: Call the Kernel health check (`curl http://localhost:8000/health` or similar).
- [ ] **Verify Viewer**: Open `http://localhost:3000` (or `http://localhost:80` via proxy) and ensure it loads the static UI.
- [ ] **Run Stress Suite**: Execute your stress tests against the local kernel endpoints.
- [ ] **Validate Invariants**: Ensure the invariant registry is correctly loaded and strictly enforced by the Kernel.

## Phase 3: Staging & Deployment
- [ ] **Deploy Staging**: Push the `kernel` and `viewer` containers to a staging environment (e.g., Render, Railway, custom VPS).
- [ ] **Multi-Operator Test**: Have multiple operators interact with the staging viewer to validate concurrency and governance locks.
- [ ] **Lock Routing Table**: Ensure production deterministic routing cannot be modified during runtime.

## Phase 4: Cut Over
- [ ] **Production Deployment**: Launch the production containers with immutable doctrine.
- [ ] **Verify Audit Logging**: Confirm all governance actions and doctrine diffs are correctly appended to the append-only logs in the data volume.
- [ ] **Retire AI Studio**: Shut down the AI Studio instance and redirect all operators to the new sovereign endpoints.
