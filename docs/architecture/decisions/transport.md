# Decisions — transport

**SignalR / HTTP / CI / auth / live-web plumbing.**

Index: [../decisions.md](../decisions.md). Rows are listed with their original line number in `decisions.md`, so a `decisions.md:<line>` citation points at the same decision it did before the decisions.md split.

| Topic | Decision |
|---|---|
| Live channel | SignalR for **both** injector and web | <!-- decisions.md:8 -->
| HTTP fallback | If injector SignalR fails to load/connect, POST `/api/events` and GET `/api/stats` still work | <!-- decisions.md:9 -->
| Server URL | Default `http://127.0.0.1:5088`. Launcher sets `FUSIONRPG_URLS` on server and `FUSIONRPG_SERVER_URL` on game (wins over BepInEx `ServerUrl` cfg) | <!-- decisions.md:15 -->
| FusionRpg update | Download `FusionRpg-win-x64.zip` from our GitHub Releases only; preserve `Server\data\`; bootstrap replace. Never download/patch the PVZ game binary | <!-- decisions.md:18 -->
| Auth | None | <!-- decisions.md:97 -->
| Third-party clients | Study only if needed; never copy foreign plugin source into this AGPL tree | <!-- decisions.md:99 -->
| CI | xUnit Core + WebApplicationFactory. Web SPA: Vitest coverage + Playwright e2e (`gk-web/web/fusion-rpg-web`). No real game / Harmony in CI | <!-- decisions.md:104 -->
| Event ingest | In-process Channel (not Memcached/Redis). Hub/`POST /api/events` ack immediately. One writer commits SQLite batches (500–1000) in a single transaction | <!-- decisions.md:106 -->
| Live web | After commit, SignalR `EventBatch` of non-noisy kinds. Damage, `bullet.init`/`bullet.place`, `item.drop`, `pet.xp` stay in SQLite only | <!-- decisions.md:107 -->
