# CineMatch — Movie Recommendation System

A student-friendly Flask project for a Software Engineering Lab project. It includes movie search, genre filters, sorting, content-based recommendations, a SQLite watchlist, JSON endpoints, unit tests, and an Azure Pipelines CI build.

## Features

- Search by movie title or description
- Filter by genre and sort by rating, release year, or title
- Movie details and content-based recommendations
- Add/remove films from a persistent local SQLite watchlist
- JSON endpoints: `/api/movies`, `/api/recommend/<movie_id>`, `/health`
- Unit tests and Azure Pipelines configuration

## Technology

- Python 3.11+
- Flask
- SQLite
- HTML/CSS
- Azure App Service (hosting) and Azure Pipelines (CI)

The included movie catalogue is a small demonstration dataset, not a live movie API. Add more records to `MOVIES` in `app.py` or integrate a licensed dataset/API for a larger catalogue.

## Run locally (Windows)

1. Install Python 3.11 or newer.
2. Open Command Prompt in this folder.
3. Create and activate a virtual environment:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the application:

   ```bat
   python app.py
   ```

6. Open `http://127.0.0.1:5000`.

## Run tests

With the virtual environment activated:

```bat
python -m unittest discover -s tests -v
```

## API examples

- `GET /health` — health check
- `GET /api/movies` — returns the movie catalogue
- `GET /api/recommend/1` — recommendations for movie ID 1
- Unknown IDs return HTTP 404

## Deploy to Azure App Service

You need an Azure subscription. Azure resources may incur charges depending on the plan you choose.

### Option A: Azure CLI (quick deployment)

1. Install Azure CLI and sign in:

   ```bash
   az login
   ```

2. From this project folder, create and deploy the web app. Choose a globally unique name:

   ```bash
   az webapp up --name YOUR-UNIQUE-APP-NAME --resource-group movie-recommendation-rg --location centralindia --runtime "PYTHON:3.11" --sku B1
   ```

   Check the available runtimes in your subscription with `az webapp list-runtimes --os linux --output table` if that runtime is not offered. App Service plan pricing varies; B1 is a paid tier.

3. If needed, set the startup command in App Service Configuration to:

   ```bash
   gunicorn --bind=0.0.0.0 --timeout 600 app:app
   ```

4. Open the app URL printed by Azure CLI.

### Important note about SQLite on Azure

SQLite is suitable for a demo, but local app storage may not be durable or shared across multiple instances in App Service. For a production or multi-instance deployment, move the watchlist to Azure SQL Database or another managed persistent database. This demo does not implement user authentication, so the watchlist is shared by anyone using the same deployment.

## Connect to Azure DevOps Pipelines

1. Push this project to a GitHub repository or Azure Repos.
2. In Azure DevOps, create a project and choose **Pipelines → New pipeline**.
3. Select your repository and choose the existing `azure-pipelines.yml`.
4. Save and run the pipeline. It installs dependencies, runs unit tests, and publishes a ZIP artifact.
5. To automate deployment as well, create an Azure Resource Manager service connection and add an Azure App Service deployment task to the pipeline. Keep secrets in Azure DevOps service connections/variable groups—never commit credentials to Git.

The included pipeline performs CI and artifact publishing; it does not automatically deploy to Azure until you configure the service connection and add a deployment step.

## Suggested Azure Boards work items

**Epic:** Movie Recommendation Platform

**Features:**
- Movie discovery and search
- Recommendation engine
- Watchlist management
- Cloud deployment and CI

**Sample user stories:**
- As a user, I want to search movies by title so I can quickly find a film.
- As a user, I want recommendations based on a selected movie so I can discover similar films.
- As a user, I want to save movies to a watchlist so I can remember what to watch.
- As a developer, I want automated tests in Azure Pipelines so changes are checked consistently.

## Security and project scope

- Change `FLASK_SECRET_KEY` to a long random secret in Azure App Settings before deployment.
- This starter project has no login, ratings submission, or per-user watchlists.
- Do not store API keys, passwords, or connection strings in source code.
