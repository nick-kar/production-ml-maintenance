# Container and hosting exercise

First complete the local workflow. Docker availability and hosted deployment have not been established on your computer.

## Docker
From the project root, with Docker installed and running:
```sh
docker build -t maintenance-ml .
docker run --rm -p 127.0.0.1:8000:8000 -v maintenance-runtime:/app/runtime maintenance-ml
```
The build trains v1 inside the pinned environment; it does not copy a host pickle. Open http://127.0.0.1:8000/docs. Stop your local API first to avoid a port conflict. The named volume preserves SQLite records after container removal. The image contains one model version. Local version changes do not alter a running container; retrain/rebuild an image for a release and retain the previous image tag for rollback. Volume ownership behavior must be verified on your Docker setup.

## Hosted milestone
Use a Docker-capable host of your choice. Before creating a service, check its current pricing and resource limits. No cloud account or billing is required for this ZIP.
1. Push code to your repository; confirm CI passes.
2. Build the Dockerfile using a container host, or push the image to a registry supported by that host.
3. Configure the container port as 8000 and health check as /health. The Docker CMD binds 0.0.0.0.
4. Configure persistent storage at /app/runtime; otherwise logs are ephemeral. One replica only for this exercise.
5. Use the host's HTTPS endpoint. Send the example prediction and record the URL, date, version and result in EVIDENCE.md.
6. Inspect application errors in host logs. The service has no authentication; use synthetic traffic only and remove the demo when finished.
7. Release a newly tagged image and then restore the previous image. Verify /health and predictions after each release.

A provider-specific exact walkthrough comes after choosing the provider. No remote deployment has been performed by delivering this project.
