-- Create the 'store' database
CREATE DATABASE store;

-- Connect to the 'store' database
\c store

CREATE SCHEMA IF NOT EXISTS store;

-- SET search_path TO store;

-- Create the 'vector' extension within the 'store' database
create extension if not exists vector with schema store;

SET search_path TO store, public;