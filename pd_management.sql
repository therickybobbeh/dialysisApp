--
-- PostgreSQL database dump
--

-- Dumped from database version 17.0
-- Dumped by pg_dump version 17.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: dialysis_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dialysis_sessions (
      id integer NOT NULL,
      patient_id integer NOT NULL,
      session_type varchar NOT NULL,
      session_id integer NOT NULL,
      weight double precision NOT NULL,
      diastolic integer NOT NULL,
      systolic integer NOT NULL,
      effluent_volume double precision NOT NULL,
      session_date timestamp without time zone NOT NULL,
      session_duration varchar,
      protein double precision NOT NULL
);


ALTER TABLE public.dialysis_sessions OWNER TO postgres;

--
-- Name: dialysis_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dialysis_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dialysis_sessions_id_seq OWNER TO postgres;

--
-- Name: dialysis_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dialysis_sessions_id_seq OWNED BY public.dialysis_sessions.id;


-- Drop existing tables and sequences to start fresh.
DROP TABLE IF EXISTS public.dialysis_sessions CASCADE;
DROP SEQUENCE IF EXISTS public.dialysis_sessions_id_seq;
DROP TABLE IF EXISTS public.food_intake CASCADE;
DROP SEQUENCE IF EXISTS public.food_intake_id_seq;
DROP TABLE IF EXISTS public.users CASCADE;
DROP SEQUENCE IF EXISTS public.users_id_seq;

-- ========================================================
-- Create tables and sequences.
-- ========================================================

CREATE TABLE public.dialysis_sessions (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    session_type varchar NOT NULL,
    session_id integer NOT NULL,
    weight double precision NOT NULL,
    diastolic integer NOT NULL,
    systolic integer NOT NULL,
    effluent_volume double precision NOT NULL,
    session_date timestamp without time zone NOT NULL,
    session_duration varchar,
    protein double precision NOT NULL
);
CREATE SEQUENCE public.dialysis_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.dialysis_sessions_id_seq OWNED BY public.dialysis_sessions.id;

CREATE TABLE public.food_intake (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    food_name character varying NOT NULL,
    protein_grams double precision NOT NULL,
    meal_time timestamp without time zone
);

CREATE SEQUENCE public.food_intake_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.food_intake_id_seq OWNED BY public.food_intake.id;

CREATE TABLE public.users (
        id integer NOT NULL,
        name character varying NOT NULL,
        email character varying NOT NULL,
        password character varying NOT NULL,
        role character varying NOT NULL,
        notifications jsonb DEFAULT '{}'::jsonb,
        patients integer[] DEFAULT '{}',
        sex character varying NOT NULL,
        height double precision NOT NULL
    );
CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;

-- Set id defaults to use the sequences.
ALTER TABLE public.dialysis_sessions ALTER COLUMN id SET DEFAULT nextval('public.dialysis_sessions_id_seq'::regclass);
ALTER TABLE public.food_intake ALTER COLUMN id SET DEFAULT nextval('public.food_intake_id_seq'::regclass);
ALTER TABLE public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);

-- ========================================================
-- Insert Data Using COPY in CSV format.
-- ========================================================

-- Insert rows into dialysis_sessions.
COPY public.dialysis_sessions (
    id,
    patient_id,
    session_type,
    session_id,
    weight,
    diastolic,
    systolic,
    effluent_volume,
    session_date,
    session_duration,
    protein
) FROM stdin WITH (FORMAT csv);
"1","1","pre","101","65.2","83","110","2.76","2025-02-18 20:18:35.525843","4 hours","23.5"
"2","1","post","102","75.8","74","115","2.60","2025-02-19 20:18:35.525843","4 hours","31.2"
"3","1","pre","103","54.6","70","114","1.77","2025-02-12 20:18:35.525843","4 hours","19.8"
"4","1","post","104","54.6","81","115","1.90","2025-02-23 20:18:35.525843","4 hours","26.1"
"5","1","pre","105","64.9","89","122","1.58","2025-02-13 20:18:35.525843","4 hours","22.4"
"6","2","post","106","62.9","78","122","2.35","2025-03-01 20:18:35.525843","4 hours","28.5"
"7","2","pre","107","63.2","80","119","2.47","2025-03-07 20:18:35.525843","4 hours","20.6"
"8","2","post","108","59.3","74","127","2.19","2025-03-06 20:18:35.525843","4 hours","29.3"
"9","2","pre","109","54.5","78","110","2.14","2025-02-11 20:18:35.525843","4 hours","18.2"
"10","2","post","110","65.0","75","121","1.98","2025-02-22 20:18:35.525843","4 hours","25.9"
"11","1","pre","111","65.2","83","110","2.76","2025-03-15 18:08:04.694401","4 hours","23.7"
"12","1","post","112","65.2","83","111","2.76","2025-02-25 20:18:35.525843","4 hours","30.0"
"14","6","pre","113","65.2","83","111","2.76","2025-02-26 20:18:35.525843","4 hours","24.8"
\.

-- Insert rows into food_intake.
COPY public.food_intake (
    id,
    patient_id,
    food_name,
    protein_grams,
    meal_time
) FROM stdin WITH (FORMAT csv);
"1","1","Grilled Chicken","35","2025-03-15 12:30:00"
"2","1","Grilled steak","40","2025-03-16 01:30:00"
\.

-- Insert rows into users.
COPY public.users (
    id,
    name,
    email,
    password,
    role,
    notifications,
    patients,
    sex,
    height
) FROM stdin WITH (FORMAT csv);
"2","Bob","bob@example.com","$argon2id$v=19$m=65536,t=3,p=4$qWDGK0tIndImSNcRfESAgQ$xnMU1+7MJ2/eBTYmAFfCDQRS5nBGFqagJ1ncU/jkkDg","patient","{}","{}","male","180.2"
"6","John Doe","johndoe@example.com","$argon2id$v=19$m=65536,t=3,p=4$/Qv9SwqQctTzoWSML1oV7Q$/fZnPd4p0yxpIuy29apYN+4LTgX8/TWKK03yMqriqYI","patient","{}","{}","male","175.0"
"1","Alice","alice@example.com","$argon2id$v=19$m=65536,t=3,p=4$g7CzL0siiYqy0UdLlzLsuQ$mM/wGHFIq83Gm/bteVs/BSOJ2VOLFIP/xBVwCfv4quw","patient","{}","{}","female","165.5"
"3","Dr. Smith","drsmith@example.com","$argon2id$v=19$m=65536,t=3,p=4$3e4wRbupvqcfUHLEGDEcMQ$Ru4hTyEcVho3WsYK7UHZ7p6QUQBdwoAC3eI04L/RYpw","provider","{}","{1,2,6}","male","175.0"
\.

-- ========================================================
-- Add constraints and indexes.
-- ========================================================
ALTER TABLE public.dialysis_sessions ADD CONSTRAINT dialysis_sessions_pkey PRIMARY KEY (id);
ALTER TABLE public.food_intake ADD CONSTRAINT food_intake_pkey PRIMARY KEY (id);
ALTER TABLE public.users ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE public.dialysis_sessions
    ADD CONSTRAINT dialysis_sessions_patient_id_fkey FOREIGN KEY (patient_id)
    REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE public.food_intake
    ADD CONSTRAINT food_intake_patient_id_fkey FOREIGN KEY (patient_id)
    REFERENCES public.users(id) ON DELETE CASCADE;