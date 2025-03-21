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
    pre_weight double precision NOT NULL,
    post_weight double precision NOT NULL,
    pre_systolic integer NOT NULL,
    pre_diastolic integer NOT NULL,
    post_systolic integer NOT NULL,
    post_diastolic integer NOT NULL,
    effluent_volume double precision NOT NULL,
    session_date timestamp without time zone NOT NULL
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


--
-- Name: food_intake; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.food_intake (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    food_name character varying NOT NULL,
    protein_grams double precision NOT NULL,
    meal_time timestamp without time zone
);


ALTER TABLE public.food_intake OWNER TO postgres;

--
-- Name: food_intake_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.food_intake_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.food_intake_id_seq OWNER TO postgres;

--
-- Name: food_intake_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.food_intake_id_seq OWNED BY public.food_intake.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying NOT NULL,
    email character varying NOT NULL,
    password character varying NOT NULL,
    role character varying NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: dialysis_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dialysis_sessions ALTER COLUMN id SET DEFAULT nextval('public.dialysis_sessions_id_seq'::regclass);


--
-- Name: food_intake id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_intake ALTER COLUMN id SET DEFAULT nextval('public.food_intake_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: dialysis_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dialysis_sessions (id, patient_id, pre_weight, post_weight, pre_systolic, pre_diastolic, post_systolic, post_diastolic, effluent_volume, session_date) FROM stdin;
1	1	65.2	54	110	83	116	75	2.76	2025-02-18 20:18:35.525843
2	1	75.8	61.9	115	74	112	78	2.6	2025-02-19 20:18:35.525843
3	1	54.6	58	114	70	100	85	1.77	2025-02-12 20:18:35.525843
4	1	54.6	68.1	115	81	116	71	1.9	2025-02-23 20:18:35.525843
5	1	64.9	53.2	122	89	113	74	1.58	2025-02-13 20:18:35.525843
6	2	62.9	48.2	122	78	116	72	2.35	2025-03-01 20:18:35.525843
7	2	63.2	69.8	119	80	116	72	2.47	2025-03-07 20:18:35.525843
8	2	59.3	49	127	74	107	79	2.19	2025-03-06 20:18:35.525843
9	2	54.5	75.8	110	78	117	78	2.14	2025-02-11 20:18:35.525843
10	2	65	72.4	121	75	117	67	1.98	2025-02-22 20:18:35.525843
11	1	65.2	54	110	83	116	75	2.76	2025-03-15 18:08:04.694401
12	1	65.2	54	111	83	116	75	2.76	2025-02-25 20:18:35.525843
14	6	65.2	54	111	83	116	75	2.76	2025-02-26 20:18:35.525843
\.


--
-- Data for Name: food_intake; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.food_intake (id, patient_id, food_name, protein_grams, meal_time) FROM stdin;
1	1	Grilled Chicken	35	2025-03-15 12:30:00
2	1	Grilled steck	40	2025-03-16 01:30:00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, name, email, password, role) FROM stdin;
2	Bob	bob@example.com	$argon2id$v=19$m=65536,t=3,p=4$qWDGK0tIndImSNcRfESAgQ$xnMU1+7MJ2/eBTYmAFfCDQRS5nBGFqagJ1ncU/jkkDg	patient
6	John Doe	johndoe@example.com	$argon2id$v=19$m=65536,t=3,p=4$/Qv9SwqQctTzoWSML1oV7Q$/fZnPd4p0yxpIuy29apYN+4LTgX8/TWKK03yMqriqYI	patient
1	Alice	alice@example.com	$argon2id$v=19$m=65536,t=3,p=4$g7CzL0siiYqy0UdLlzLsuQ$mM/wGHFIq83Gm/bteVs/BSOJ2VOLFIP/xBVwCfv4quw	patient
3	Dr. Smith	drsmith@example.com	$argon2id$v=19$m=65536,t=3,p=4$3e4wRbupvqcfUHLEGDEcMQ$Ru4hTyEcVho3WsYK7UHZ7p6QUQBdwoAC3eI04L/RYpw	provider
\.


--
-- Name: dialysis_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dialysis_sessions_id_seq', 14, true);


--
-- Name: food_intake_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.food_intake_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: dialysis_sessions dialysis_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dialysis_sessions
    ADD CONSTRAINT dialysis_sessions_pkey PRIMARY KEY (id);


--
-- Name: food_intake food_intake_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_intake
    ADD CONSTRAINT food_intake_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_dialysis_sessions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dialysis_sessions_id ON public.dialysis_sessions USING btree (id);


--
-- Name: ix_food_intake_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_food_intake_id ON public.food_intake USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: dialysis_sessions dialysis_sessions_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dialysis_sessions
    ADD CONSTRAINT dialysis_sessions_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: food_intake food_intake_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_intake
    ADD CONSTRAINT food_intake_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

