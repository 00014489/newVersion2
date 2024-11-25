--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)

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
-- Name: update_deadline_at(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_deadline_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Case 1: For new user (INSERT), set deadline_at to current date + 7 days
    IF TG_OP = 'INSERT' THEN
        NEW.deadline_at := CURRENT_TIMESTAMP + INTERVAL '3 days';

    -- Case 2: For existing user (UPDATE), if status is TRUE, set deadline_at to current date + 30 days
    ELSIF TG_OP = 'UPDATE' AND NEW.status = TRUE THEN
        NEW.deadline_at := CURRENT_TIMESTAMP + INTERVAL '30 days';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_deadline_at() OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.status = FALSE THEN
        NEW.updated_at := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: input_file; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.input_file (
    id integer NOT NULL,
    file_id character varying(255) NOT NULL,
    out_0_id integer DEFAULT 0,
    out_15_id integer DEFAULT 0,
    out_50_id integer DEFAULT 0,
    file_name character varying(255) NOT NULL,
    file_name_original character varying(255)
);


ALTER TABLE public.input_file OWNER TO postgres;

--
-- Name: input_file_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.input_file_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.input_file_id_seq OWNER TO postgres;

--
-- Name: input_file_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.input_file_id_seq OWNED BY public.input_file.id;


--
-- Name: linksyou; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.linksyou (
    id integer NOT NULL,
    links text,
    duration integer DEFAULT 0,
    chatid bigint DEFAULT 0,
    messageid bigint DEFAULT 0
);


ALTER TABLE public.linksyou OWNER TO postgres;

--
-- Name: linksyou_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.linksyou_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.linksyou_id_seq OWNER TO postgres;

--
-- Name: linksyou_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.linksyou_id_seq OWNED BY public.linksyou.id;


--
-- Name: order_list; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_list (
    id integer NOT NULL,
    url_id bigint NOT NULL,
    status boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.order_list OWNER TO postgres;

--
-- Name: order_list_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_list_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_list_id_seq OWNER TO postgres;

--
-- Name: order_list_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_list_id_seq OWNED BY public.order_list.id;


--
-- Name: out_0; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.out_0 (
    id integer NOT NULL,
    chat_id bigint NOT NULL,
    message_id bigint NOT NULL
);


ALTER TABLE public.out_0 OWNER TO postgres;

--
-- Name: out_0_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.out_0_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.out_0_id_seq OWNER TO postgres;

--
-- Name: out_0_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.out_0_id_seq OWNED BY public.out_0.id;


--
-- Name: out_15; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.out_15 (
    id integer NOT NULL,
    chat_id bigint NOT NULL,
    message_id bigint NOT NULL
);


ALTER TABLE public.out_15 OWNER TO postgres;

--
-- Name: out_15_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.out_15_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.out_15_id_seq OWNER TO postgres;

--
-- Name: out_15_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.out_15_id_seq OWNED BY public.out_15.id;


--
-- Name: out_50; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.out_50 (
    id integer NOT NULL,
    chat_id bigint NOT NULL,
    message_id bigint NOT NULL
);


ALTER TABLE public.out_50 OWNER TO postgres;

--
-- Name: out_50_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.out_50_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.out_50_id_seq OWNER TO postgres;

--
-- Name: out_50_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.out_50_id_seq OWNED BY public.out_50.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    user_name character varying(255) DEFAULT 'noUserName'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status boolean DEFAULT true,
    deadline_at timestamp without time zone
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
-- Name: input_file id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_file ALTER COLUMN id SET DEFAULT nextval('public.input_file_id_seq'::regclass);


--
-- Name: linksyou id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.linksyou ALTER COLUMN id SET DEFAULT nextval('public.linksyou_id_seq'::regclass);


--
-- Name: order_list id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_list ALTER COLUMN id SET DEFAULT nextval('public.order_list_id_seq'::regclass);


--
-- Name: out_0 id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.out_0 ALTER COLUMN id SET DEFAULT nextval('public.out_0_id_seq'::regclass);


--
-- Name: out_15 id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.out_15 ALTER COLUMN id SET DEFAULT nextval('public.out_15_id_seq'::regclass);


--
-- Name: out_50 id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.out_50 ALTER COLUMN id SET DEFAULT nextval('public.out_50_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: input_file; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.input_file (id, file_id, out_0_id, out_15_id, out_50_id, file_name, file_name_original) FROM stdin;
\.


--
-- Data for Name: linksyou; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.linksyou (id, links, duration, chatid, messageid) FROM stdin;
\.


--
-- Data for Name: order_list; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_list (id, url_id, status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: out_0; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.out_0 (id, chat_id, message_id) FROM stdin;
\.


--
-- Data for Name: out_15; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.out_15 (id, chat_id, message_id) FROM stdin;
\.


--
-- Data for Name: out_50; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.out_50 (id, chat_id, message_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, user_id, user_name, created_at, status, deadline_at) FROM stdin;
5	708345655	just_blessed	2024-11-15 03:20:38.639118	t	2024-12-22 02:02:22.66294
7	631142963	jonibek_toirov	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
9	5154345737	Firdavs_2102	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
11	1671246599	Studentofwiut	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
8	6676871794	saidalo_005	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
14	1442936958	jabborov_bek05	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
15	1655474797	olfrnz	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
16	5781325887	buriniyozov	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
17	5075674162	vohidoov7	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
18	1706272244	sharyar_usenov	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
19	1027483761	memoli_11	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
20	2075488703	jyakhyoev	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
22	1925977530	Azizkhon_Ikhtiyorov	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
23	1613779386	hikmatovvs	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
25	5129472682	Yonmi_73	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
26	6096352298	shahnoza_1805	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
27	1932950886	erkinov_safarbek	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
28	790697152	Santos_Scott	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
30	5216422759	Westminsterrguy	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
32	979443888	Shokha7	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
33	5837237033	muzaffarnurmetov	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
34	1193655512	XXXursandev	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
38	7210241524	nixsei	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
40	6193605299	B_One005	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
41	2084059749	komilov05n	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
43	5807991563	rsmvrr	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
46	6657665213	farkhadja_n	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
47	5146371510	Sherqulov_Sardorbek	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
49	1104932030	Wiutguy	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
50	764692165	M_yusufova	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
51	5625872174	shohruh_frontend	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
53	217332503	jurabeksodikov	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
24	857547937	eshnorov_sunnat	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
55	5017799215	stuffed_0307	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
57	2122933575	Fxx6100	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
58	1446365032	K_narg1z	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
60	1958101551	smglll	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
61	838717833	jonny2005	2024-11-15 03:20:38.639118	t	2024-12-18 17:12:17.441912
44	1912498359	just_0zod	2024-11-15 03:20:38.639118	f	2024-12-22 02:32:11.936776
73	1081599122	TR_bOts_Admin	2024-11-15 16:05:00.826771	t	2024-12-24 23:47:35.687409
52	445800405	rikkudo_sennin	2024-11-15 03:20:38.639118	t	2024-12-21 12:06:42.879795
1	1031267509	Usmonov_Elbek	2024-11-15 03:20:38.639118	t	2024-12-22 01:35:04.522817
103	624716214	kuronboev_975	2024-11-22 01:40:22.446649	t	2024-11-29 01:40:22.446649
48	6500677674	erkinov_xlx	2024-11-15 03:20:38.639118	t	2024-12-22 01:45:56.174694
\.


--
-- Name: input_file_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.input_file_id_seq', 1, false);


--
-- Name: linksyou_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.linksyou_id_seq', 1, false);


--
-- Name: order_list_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_list_id_seq', 1, false);


--
-- Name: out_0_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.out_0_id_seq', 1, false);


--
-- Name: out_15_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.out_15_id_seq', 1, false);


--
-- Name: out_50_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.out_50_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 112, true);


--
-- Name: input_file input_file_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_file
    ADD CONSTRAINT input_file_pkey PRIMARY KEY (id);


--
-- Name: linksyou linksyou_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.linksyou
    ADD CONSTRAINT linksyou_pkey PRIMARY KEY (id);


--
-- Name: order_list order_list_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_list
    ADD CONSTRAINT order_list_pkey PRIMARY KEY (id);


--
-- Name: out_0 out_0_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.out_0
    ADD CONSTRAINT out_0_pkey PRIMARY KEY (id);


--
-- Name: out_15 out_15_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.out_15
    ADD CONSTRAINT out_15_pkey PRIMARY KEY (id);


--
-- Name: out_50 out_50_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.out_50
    ADD CONSTRAINT out_50_pkey PRIMARY KEY (id);


--
-- Name: users unique_user_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_user_id UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users set_deadline_at_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER set_deadline_at_trigger BEFORE INSERT OR UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_deadline_at();


--
-- Name: order_list set_updated_at_on_status_false; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER set_updated_at_on_status_false BEFORE UPDATE ON public.order_list FOR EACH ROW WHEN ((old.status IS DISTINCT FROM new.status)) EXECUTE FUNCTION public.update_updated_at_column();


--
-- PostgreSQL database dump complete
--

