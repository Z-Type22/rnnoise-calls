# rnnoise-calls

> Server-side service for noise suppression in voice calls using RNNoise

- **rnnoise-calls** is a backend service designed to integrate real-time noise suppression into a WebRTC-based calling system.  
- It is built on top of the **RNNoise**.

---

## Structure

```
rnnoise-calls/         # Project
├── migrations/        # Alembic migrations
├── src/               # Core project
│   ├── auth/          # Auth module
│   ├── calls/         # Calls module
│   └── users/         # Users module
├── docker-compose.yml # Docker services
├── .env.example       # Env template
├── Dockerfile         # Docker configuration
├── Makefile           # Build file
├── pyproject.toml     # Python env
├── generate_keys.py   # Generate keys for jwt (example: for windows)
└── README.md          # Readme file
```

## Run

- **make init** — Project initialization
- **make build** — Project build
- **make up** — Project up (to be done after each `git pull`).  
  _Future improvement: implement CI/CD pipelines_
- **make migrate** — Apply migrations
- **make down** — Stop and remove all Docker containers
