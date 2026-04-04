# Horizon Protocol Migration Checklist

## Operational Cutover Sequence (AI Studio → Sovereign)

### Phase 1: Pre-Migration (T-72h)
- [ ] Host provisioned
- [ ] Docker ready
- [ ] DNS configured
- [ ] `.env` locked
- [ ] TLS cert staged

### Phase 2: Data Export (T-48h)
- [ ] Doctrine files exported + checksummed
- [ ] Memory migrated
- [ ] Config parity mapped

### Phase 3: Build & Deploy (T-24h)
- [ ] Local build
- [ ] Smoke test
- [ ] Alembic migrations
- [ ] Production deploy
- [ ] TLS verify

### Phase 4: Verification Gate (T-12h)
- [ ] Full functional suite run
- [ ] Determinism parity test (hash + replay)
- [ ] Performance baseline established
- [ ] Security audit complete

### Phase 5: Cutover (T-0)
- [ ] 10-step atomic switch:
  1. AI Studio set to read-only
  2. Final data export
  3. Load final data into Sovereign
  4. Verify final data parity
  5. DNS flip
  6. Monitor traffic
  7. Confirm live status
  8. (Internal Steps)
  9. (Internal Steps)
  10. Sovereign Protocol Active

### Phase 6: Post-Hardening (T+7d)
- [ ] Backups enabled
- [ ] Alerts configured
- [ ] Chain writes enabled
- [ ] AI Studio deprecated

---

## Rollback Triggers (Any one = Revert)
- [ ] 5xx errors > 5% for 5 min
- [ ] p95 latency > 2x baseline for 10 min
- [ ] Hash determinism failure
- [ ] Data loss detected
- [ ] WebSocket success rate < 90%
