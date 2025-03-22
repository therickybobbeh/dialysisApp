# PeritonealDialysisApp
Peritoneal Dialysis (PD) management application

![Login page](https://github.gatech.edu/lalkhalil3/PeritonealDialysisApp/assets/90599/d280a85d-a77a-4ade-87fd-a0ff0eb8ab43)


1. Project Overview
The Peritoneal Dialysis (PD) Management App is designed to help patients and providers monitor and manage peritoneal dialysis treatment. The application allows patients to log their health data, provides analytics for trend monitoring, and enables providers to make informed treatment decisions.

1.1 Features

•	Patient Module:

o	Input and track dialysis session details (weight, blood pressure, effluent volume).

o	Monitor trends and receive alerts for negative patterns.

o	Log daily meals and track protein intake.

•	Provider Module:

o	Dashboard to track patient data and identify high-risk cases.

o	View analytics and adjust treatment recommendations.

•	Security & Authentication:

o	OAuth2-based authentication with JWT.

o	Role-based access control (patients, providers).

•	Deployment:

o	backend (FastAPI).

o	Frontend built with React (Next.js).

o	PostgreSQL database.

o	Dockerized deployment.

2. API Contract
![Swagger doc of the backend APIs](https://github.gatech.edu/lalkhalil3/PeritonealDialysisApp/assets/90599/4e4b4aea-5c09-413c-be3f-3ee500442a9b)

2.1 Authentication Endpoints

•	POST /auth/register – Register new users.

•	POST /auth/login – Authenticate users and return JWT.

•	POST /auth/logout – Invalidate session.

2.2 Patient Endpoints

•	POST /patients/{id}/dialysis-session – Log dialysis session.

•	GET /patients/{id}/dialysis-history – Retrieve dialysis history.

•	POST /patients/{id}/meal-log – Log meals and protein intake.

•	GET /patients/{id}/nutrition-summary – Get daily protein intake summary.

2.3 Provider Endpoints

•	GET /providers/dashboard – View all patients' status.

•	GET /patients/{id}/risk-analysis – Fetch analytics and flag high-risk cases.

•	PUT /patients/{id}/treatment-plan – Update treatment plan.

3. Database Schema (PostgreSQL)

3.1 Tables

-users

-dialysis_sessions

-food_intake

![pd_managment_DB](https://github.gatech.edu/lalkhalil3/PeritonealDialysisApp/assets/90599/eeafc7b5-af00-48a8-84b6-08d612f608c5)

# To build and run the App locally:

Backend:

```
pip install -r requirements.txt

uvicorn app.api.main:app  --reload --host 0.0.0.0 --port 8004 --log-level debug


```

Frontend:

```
npm install
npm run build
npm run dev

``` 

Hapi FHIR Server:

```
running at:

http://localhost:8080
```

# To run the App as a Docker container:

- Assuming you have docker installed and setup on your machince.


```
to start the container run:

docker-compose up --build

to stop the container run:

docker-compose down

```
![Docker containers](https://github.gatech.edu/lalkhalil3/PeritonealDialysisApp/assets/90599/08b4ebd4-c7df-4554-a210-911985eb7e31)

# Swagger Specs: http://localhost:8004/docs#/
# Backend APIs URL: http://localhost:8004/
# Frontend- React URL: http://localhost:3000/


# Flow diagram:

```mermaid

flowchart TD

    %% CLIENT SIDE
    subgraph ClientBrowser["Patient / Provider Browser"]
        LoginForm[Login Form]
        Dashboard[Dashboard]
        DialysisForm[Dialysis Form]
        UI[React Frontend - Next.js]

        LoginForm -->|POST /auth/token| UI
        Dashboard -->|GET /dialysis/analytics| UI
        DialysisForm -->|POST /dialysis/sessions| UI
    end

    %% FRONTEND CONTAINER
    subgraph Frontend["Frontend - React Docker Container"]
        UI
    end

    %% BACKEND CONTAINER
    subgraph Backend["Backend - FastAPI Docker Container"]
        API[FastAPI App]
        Auth[Auth Routes - /auth/token and /auth/register]
        Dialysis[Dialysis Routes - /dialysis/sessions and /analytics]
        Seeder[Seeder Script]
        Alembic[Alembic Migrations]

        API --> Auth
        API --> Dialysis
        API --> Seeder
        API --> Alembic
    end

    %% DATABASE CONTAINER
    subgraph Database["PostgreSQL Docker Container"]
        DB[(pd_management)]
        Tables[users, dialysis_sessions, food_intake]
    end

    %% CONNECTIONS
    UI -->|Fetch token, store JWT and user_id| Auth
    UI -->|Submit dialysis data| Dialysis
    UI -->|Fetch analytics and live updates| Dialysis
    Dialysis -->|SQLAlchemy Queries| DB
    Auth -->|JWT creation and validation| DB
    Seeder -->|Insert dummy data| DB
    Alembic -->|Run migrations| DB

    %% DOCKER COMPOSE
    subgraph DockerCompose["docker-compose"]
        frontendService[frontend service]
        backendService[backend service]
        dbService[postgres service]

        frontendService --> Frontend
        backendService --> Backend
        dbService --> Database

        frontendService --> backendService
        backendService --> dbService
    end


```
