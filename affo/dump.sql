--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3
-- Dumped by pg_dump version 12.3

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

--
-- Name: adminpack; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION adminpack; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: air; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.air (
    id integer NOT NULL,
    flying_fortresses integer DEFAULT 0 NOT NULL,
    fighter_jets integer DEFAULT 0 NOT NULL,
    apaches integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.air OWNER TO postgres;

--
-- Name: coalitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coalitions (
    colid integer NOT NULL,
    userid integer NOT NULL
);


ALTER TABLE public.coalitions OWNER TO postgres;

--
-- Name: colnames; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.colnames (
    id integer NOT NULL,
    leader integer NOT NULL,
    description character varying(240),
    type character varying(12) NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.colnames OWNER TO postgres;

--
-- Name: colnames_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.colnames ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.colnames_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ground; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ground (
    id integer NOT NULL,
    soldiers integer DEFAULT 0 NOT NULL,
    artillery integer DEFAULT 0 NOT NULL,
    tanks integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.ground OWNER TO postgres;

--
-- Name: offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.offers (
    offer_id integer NOT NULL,
    user_id integer NOT NULL,
    resource character varying(50) NOT NULL,
    amount integer NOT NULL,
    price integer NOT NULL
);


ALTER TABLE public.offers OWNER TO postgres;

--
-- Name: offers_offer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.offers ALTER COLUMN offer_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.offers_offer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: provinces; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provinces (
    userid integer NOT NULL,
    provinceid integer NOT NULL,
    provincename character varying(240),
    citycount integer DEFAULT 1 NOT NULL,
    land integer DEFAULT 100 NOT NULL,
    population integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.provinces OWNER TO postgres;

--
-- Name: provinces_provinceid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.provinces ALTER COLUMN provinceid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.provinces_provinceid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.requests (
    reqid integer NOT NULL,
    colid integer NOT NULL,
    message character varying(240)
);


ALTER TABLE public.requests OWNER TO postgres;

--
-- Name: resources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resources (
    id integer NOT NULL,
    gold integer DEFAULT 0 NOT NULL,
    plutonium integer DEFAULT 0 NOT NULL,
    consumer_goods integer DEFAULT 0 NOT NULL,
    uranium integer DEFAULT 0 NOT NULL,
    thorium integer DEFAULT 0 NOT NULL,
    iron integer DEFAULT 0 NOT NULL,
    coal integer DEFAULT 0 NOT NULL,
    oil integer DEFAULT 0 NOT NULL,
    lead integer DEFAULT 0 NOT NULL,
    silicon integer DEFAULT 0 NOT NULL,
    copper integer DEFAULT 0 NOT NULL,
    bauxite integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.resources OWNER TO postgres;

--
-- Name: special; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.special (
    id integer NOT NULL,
    spies integer DEFAULT 0 NOT NULL,
    icbms integer DEFAULT 0 NOT NULL,
    nukes integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.special OWNER TO postgres;

--
-- Name: stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stats (
    id integer NOT NULL,
    population integer DEFAULT 100 NOT NULL,
    happiness integer DEFAULT 20 NOT NULL,
    location character varying(100),
    gold integer DEFAULT 1000 NOT NULL
);


ALTER TABLE public.stats OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(60) NOT NULL,
    email character varying(100) NOT NULL,
    date character varying(10) NOT NULL,
    hash character varying(255) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: water; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.water (
    id integer NOT NULL,
    destroyers integer DEFAULT 0 NOT NULL,
    cruisers integer DEFAULT 0 NOT NULL,
    submarines integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.water OWNER TO postgres;

--
-- Data for Name: air; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.air (id, flying_fortresses, fighter_jets, apaches) FROM stdin;
\.


--
-- Data for Name: coalitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coalitions (colid, userid) FROM stdin;
\.


--
-- Data for Name: colnames; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.colnames (id, leader, description, type, name) FROM stdin;
\.


--
-- Data for Name: ground; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ground (id, soldiers, artillery, tanks) FROM stdin;
\.


--
-- Data for Name: offers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.offers (offer_id, user_id, resource, amount, price) FROM stdin;
\.


--
-- Data for Name: provinces; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provinces (userid, provinceid, provincename, citycount, land, population) FROM stdin;
\.


--
-- Data for Name: requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.requests (reqid, colid, message) FROM stdin;
\.


--
-- Data for Name: resources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.resources (id, gold, plutonium, consumer_goods, uranium, thorium, iron, coal, oil, lead, silicon, copper, bauxite) FROM stdin;
\.


--
-- Data for Name: special; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.special (id, spies, icbms, nukes) FROM stdin;
\.


--
-- Data for Name: stats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stats (id, population, happiness, location, gold) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, date, hash) FROM stdin;
\.


--
-- Data for Name: water; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.water (id, destroyers, cruisers, submarines) FROM stdin;
\.


--
-- Name: colnames_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.colnames_id_seq', 1, false);


--
-- Name: offers_offer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.offers_offer_id_seq', 1, false);


--
-- Name: provinces_provinceid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.provinces_provinceid_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: air air_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.air
    ADD CONSTRAINT air_pkey PRIMARY KEY (id);


--
-- Name: coalitions coalitions_userid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coalitions
    ADD CONSTRAINT coalitions_userid_key UNIQUE (userid);


--
-- Name: colnames colnames_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.colnames
    ADD CONSTRAINT colnames_name_key UNIQUE (name);


--
-- Name: colnames colnames_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.colnames
    ADD CONSTRAINT colnames_pkey PRIMARY KEY (id);


--
-- Name: ground ground_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ground
    ADD CONSTRAINT ground_pkey PRIMARY KEY (id);


--
-- Name: offers offers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.offers
    ADD CONSTRAINT offers_pkey PRIMARY KEY (offer_id);


--
-- Name: provinces provinces_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.provinces
    ADD CONSTRAINT provinces_pkey PRIMARY KEY (provinceid);


--
-- Name: resources resources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resources
    ADD CONSTRAINT resources_pkey PRIMARY KEY (id);


--
-- Name: special special_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.special
    ADD CONSTRAINT special_pkey PRIMARY KEY (id);


--
-- Name: stats stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stats
    ADD CONSTRAINT stats_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: water water_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.water
    ADD CONSTRAINT water_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

