--
-- Name: working_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE working_temp (
    biosamplelist integer,
    biosampleob integer,
    inclusioncomment character varying(64),
    addeddate date,
    addedby character varying(256)
);


ALTER TABLE public.working_temp OWNER TO agrbrdf;

