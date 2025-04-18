-- 1) Drop any existing objects
DROP TABLE IF EXISTS public.dialysis_sessions CASCADE;
DROP SEQUENCE IF EXISTS public.dialysis_sessions_id_seq;
DROP TABLE IF EXISTS public.food_intake CASCADE;
DROP SEQUENCE IF EXISTS public.food_intake_id_seq;
DROP TABLE IF EXISTS public.users CASCADE;
DROP SEQUENCE IF EXISTS public.users_id_seq;

-- 2) Create users table + sequence
CREATE TABLE public.users (
    id            integer      NOT NULL,
    name          varchar      NOT NULL,
    email         varchar      NOT NULL,
    password      varchar      NOT NULL,
    role          varchar      NOT NULL,
    notifications jsonb        DEFAULT '{}'::jsonb,
    patients      integer[]    DEFAULT '{}',
    sex           varchar      NOT NULL,
    height        double precision NOT NULL
);
CREATE SEQUENCE public.users_id_seq
    AS integer START WITH 1 INCREMENT BY 1 CACHE 1;
ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
ALTER TABLE public.users
    ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq');

-- 3) Load users (CSV, with proper quoting)
COPY public.users (
    id,name,email,password,role,notifications,patients,sex,height
) FROM stdin WITH (FORMAT csv);
1,"Alice",alice@example.com,"$argon2id$…","patient","{""lowBloodPressure"":false,""highBloodPressure"":true,""dialysisGrowthAdjustment"":false,""fluidOverloadHigh"":true,""fluidOverloadWatch"":false,""effluentVolume"":true,""protein"":true}","{}",female,165.5
2,"Bob",bob@example.com,"$argon2id$…","patient","{""lowBloodPressure"":false,""highBloodPressure"":true,""dialysisGrowthAdjustment"":false,""fluidOverloadHigh"":true,""fluidOverloadWatch"":false,""effluentVolume"":true,""protein"":true}","{}",male,180.2
3,"Dr. Smith",drsmith@example.com,"$argon2id$…","provider","{}","{1,2,6}",male,175.0
\.

-- bump users sequence
SELECT setval('public.users_id_seq', COALESCE((SELECT MAX(id) FROM public.users), 1) + 1, false);

-- 4) Create dialysis_sessions & food_intake + sequences
CREATE TABLE public.dialysis_sessions (
    id               integer      NOT NULL,
    patient_id       integer      NOT NULL,
    session_type     varchar      NOT NULL,
    session_id       integer      NOT NULL,
    weight           double precision NOT NULL,
    diastolic        integer      NOT NULL,
    systolic         integer      NOT NULL,
    effluent_volume  double precision NOT NULL,
    session_date     timestamp    NOT NULL,
    session_duration varchar,
    protein          double precision NOT NULL
);
CREATE SEQUENCE public.dialysis_sessions_id_seq
    AS integer START WITH 1 INCREMENT BY 1 CACHE 1;
ALTER SEQUENCE public.dialysis_sessions_id_seq OWNED BY public.dialysis_sessions.id;
ALTER TABLE public.dialysis_sessions
    ALTER COLUMN id SET DEFAULT nextval('public.dialysis_sessions_id_seq');

CREATE TABLE public.food_intake (
    id            integer      NOT NULL,
    patient_id    integer      NOT NULL,
    food_name     varchar      NOT NULL,
    protein_grams double precision NOT NULL,
    meal_time     timestamp
);
CREATE SEQUENCE public.food_intake_id_seq
    AS integer START WITH 1 INCREMENT BY 1 CACHE 1;
ALTER SEQUENCE public.food_intake_id_seq OWNED BY public.food_intake.id;
ALTER TABLE public.food_intake
    ALTER COLUMN id SET DEFAULT nextval('public.food_intake_id_seq');

-- 5) Load dialysis_sessions (quote “4 hours”)
COPY public.dialysis_sessions (
    id,patient_id,session_type,session_id,weight,diastolic,systolic,effluent_volume,session_date,session_duration,protein
) FROM stdin WITH (FORMAT csv);
1,1,pre,101,65.2,83,110,2.76,2025-02-18 20:18:35,"4 hours",23.5
2,1,post,102,75.8,74,115,2.60,2025-02-19 20:18:35,"4 hours",31.2
\.

SELECT setval('public.dialysis_sessions_id_seq', COALESCE((SELECT MAX(id) FROM public.dialysis_sessions), 1) + 1, false);

-- 6) Load food_intake
COPY public.food_intake (
    id,patient_id,food_name,protein_grams,meal_time
) FROM stdin WITH (FORMAT csv);
1,1,"Grilled Chicken",35,2025-03-15 12:30:00
2,1,"Grilled Steak",40,2025-03-16 01:30:00
\.

SELECT setval('public.food_intake_id_seq', COALESCE((SELECT MAX(id) FROM public.food_intake), 1) + 1, false);

-- 7) Add PKs and FKs
ALTER TABLE public.users ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE public.dialysis_sessions ADD CONSTRAINT dialysis_sessions_pkey PRIMARY KEY (id);
ALTER TABLE public.dialysis_sessions
  ADD CONSTRAINT dialysis_sessions_patient_id_fkey
  FOREIGN KEY (patient_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE public.food_intake ADD CONSTRAINT food_intake_pkey PRIMARY KEY (id);
ALTER TABLE public.food_intake
  ADD CONSTRAINT food_intake_patient_id_fkey
  FOREIGN KEY (patient_id) REFERENCES public.users(id) ON DELETE CASCADE;