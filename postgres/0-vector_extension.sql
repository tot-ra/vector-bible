-- Create the 'store' database
CREATE DATABASE store;

-- Connect to the 'store' database
\c store

CREATE SCHEMA IF NOT EXISTS store;

SET search_path TO store;

-- Create the 'vector' extension within the 'store' database
CREATE EXTENSION IF NOT EXISTS vector;


-- Create the 'embeddings' table within the 'store' schema
CREATE TABLE store.embeddings (
  id SERIAL PRIMARY KEY,
  embedding vector,
  text text,
  created_at timestamptz DEFAULT now()
);