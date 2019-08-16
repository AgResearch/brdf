--
-- Name: t_sample_fact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE t_sample_fact (
    labid character varying(20),
    sampleid character varying(40),
    sample_type character varying(20),
    animalid integer,
    mixid integer,
    ownerid integer,
    date_received character varying(20),
    restricted_use character varying(10),
    sys_created character varying(20),
    sys_createdby character varying(20),
    max_kgd_sampdepth double precision,
    biosubjectob integer
);


ALTER TABLE public.t_sample_fact OWNER TO agrbrdf;

