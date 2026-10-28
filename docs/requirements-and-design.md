# Movie Recommendation System — Requirements and Design

## Aim
Develop a movie discovery and recommendation web application and prepare it for deployment using Microsoft Azure services and Azure DevOps.

## Functional requirements
1. The user can view the movie catalogue.
2. The user can search by title or description.
3. The user can filter by genre.
4. The user can sort by rating, year, or title.
5. The user can view movie details.
6. The system can recommend similar films using shared genres and tags.
7. The user can add and remove movies from a watchlist.
8. The application exposes a health endpoint and JSON endpoints for movie data and recommendations.

## Non-functional requirements
- Simple responsive browser interface.
- Validate unknown movie IDs and return HTTP 404.
- Use parameterized SQL queries for watchlist operations.
- Automated tests cover core routes and recommendation behavior.
- Source code is version-controlled and can be built in Azure Pipelines.

## Architecture
Browser → Flask routes/controllers → recommendation logic and movie catalogue → SQLite watchlist database.

Azure deployment: Git repository → Azure Pipelines (install, test, package) → published artifact. A separate App Service deployment task can be configured with an Azure service connection.

## Recommendation approach
For each candidate movie, score shared genres (3 points each), shared tags (1 point each), and add a small rating tie-break contribution (rating / 10). The selected movie is excluded. Candidates are sorted by score and rating, then the top six are returned. This is a transparent content-based baseline, not a trained machine-learning model.

## Sample test cases

| ID | Scenario | Expected result |
|---|---|---|
| TC01 | Open homepage | HTTP 200 and movie catalogue rendered |
| TC02 | Search for Inception | Matching movie is shown |
| TC03 | Search for a non-existent title | Empty-state message appears |
| TC04 | Request recommendations for movie ID 1 | HTTP 200 with recommendation list |
| TC05 | Request unknown movie ID | HTTP 404 |
| TC06 | Add movie to watchlist | Movie appears on watchlist page |
| TC07 | Remove movie from watchlist | Movie disappears from watchlist |
| TC08 | Call health endpoint | JSON status is healthy |

## Scope limitations
The starter uses a small embedded catalogue, has no authentication, and uses one shared watchlist. A full production version should use a larger licensed dataset or a movie API, user identity, and a managed database such as Azure SQL.
