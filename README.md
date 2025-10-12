# AirGuardian Backend - Mini Version

A real-time drone monitoring system designed to protect critical infrastructure by detecting unauthorized drone incursions into a designated No-Fly Zone (NFZ). This FastAPI-based backend service periodically fetches drone position data, checks for violations, stores them in a database, and exposes API endpoints for data retrieval.

## Features

- **Real-time Monitoring:** Fetches drone positions data every 10 seconds using external API.
- **NFZ Violation Detection:** Detects drones that enter the 1,000-unit radius No-Fly Zone centered at `[0, 0]`.
- **Violation Storage:** Stores violations in PostgreSQL with owner details.
- **Security:** Protects sensitive violation data with a secret header authentication mechanism.
- **Containerized:** Fully Dockerized setup for easy development and deployment.
- **Test Automation:** Comprehensive test suite with pytest.
- **API Endpoints:** 
  - `/health` - Service status
  - `/drones` - Live drone positions
  - `/nfz` - Recent violations (secured with API secret)

## Tech Stack

-   **Framework:** FastAPI
-   **Task Queue:** Celery
-   **Database:** PostgreSQL
-   **Message Broker:** Redis
-   **Containerization:** Docker & Docker Compose
-   **Python Dependency Management:** Poetry
-   **Testing:** Pytest, HTTPX, pytest-cov

## 📋 Prerequisites

Ensure you have the following installed on your system:
-   Docker
-   Docker Compose
## ⚙️ Quick Start

### Method 1: Using Docker Compose (Recommended)
1.  **Clone the repository:**
    ```bash
    ```
