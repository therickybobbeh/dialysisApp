# Use official Python image as a base
FROM python:3.11

# Install PostgreSQL client (for `pg_isready` and `psql`)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app  

#  Copy the .env file explicitly
COPY .env /app/.env

#  Copy and install dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

#  Copy the backend application code
COPY backend /app/backend  

#  Copy the database SQL file (if available)
COPY pd_management.sql /app/pd_management.sql

#  Copy the seeder script separately
COPY backend/scripts/seeder.py /app/backend/scripts/seeder.py

#  Copy the entrypoint script
COPY backend/scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh  # Make it executable

# Set the working directory to the backend directory
WORKDIR /app/backend 

#  Expose the correct API port
EXPOSE 8004

# Use entrypoint script to handle migrations and database restore
ENTRYPOINT ["/app/entrypoint.sh"]
