# Landslide Risk Monitoring System - Database Documentation

This directory contains the database design, schema definitions, seed data, and performance-optimized queries for the **AI-Based Landslide Risk Monitoring System (SIH 2026)**.

## Files

- `schema.sql`: Production-ready PostgreSQL / Supabase DDL schema. Contains tables, foreign keys, cascading constraints, check constraints, and performance indexes.
- `seed.sql`: Realistic demonstration dataset covering 24 high-hazard and moderate-hazard locations across Northeast India (Assam, Meghalaya, Sikkim, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura) with time-series environmental data, AI risk predictions, alerts, and historical landslide events.
- `queries.sql`: Optimized SQL queries for dashboard KPIs, map feeds, risk distribution, state summaries, and historical charts.

## Running on Supabase

1. Open your [Supabase Project Dashboard](https://supabase.com/dashboard).
2. Go to the **SQL Editor** in the left sidebar.
3. Paste and execute the contents of `schema.sql`.
4. Paste and execute the contents of `seed.sql`.
5. Copy your connection string from **Project Settings > Database > Connection string (URI)**.
6. Set `DATABASE_URL` in your backend `.env` file:
   ```env
   DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
   ```

## Running on Local PostgreSQL

1. Ensure PostgreSQL is installed and running.
2. Create the database:
   ```bash
   createdb -U postgres landslide_db
   ```
3. Run the schema and seed scripts:
   ```bash
   psql -U postgres -d landslide_db -f schema.sql
   psql -U postgres -d landslide_db -f seed.sql
   ```
4. Set the `DATABASE_URL` in your `.env`:
   ```env
   DATABASE_URL="postgresql://postgres:password@localhost:5432/landslide_db"
   ```

## Running with Local SQLite (Default Dev Mode)

The FastAPI application is equipped with automatic SQLite fallback when using:
```env
DATABASE_URL="sqlite:///./landslide_risk.db"
```
The application will automatically initialize all tables and seed data upon startup.
