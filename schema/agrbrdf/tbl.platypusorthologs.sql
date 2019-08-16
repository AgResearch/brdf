--
-- Name: platypusorthologs; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE platypusorthologs (
    orthogene character varying(2048),
    wallabyortholog integer,
    platypusortholog integer,
    humanplacentalortholog integer,
    cattleplacentalortholog integer
);


ALTER TABLE public.platypusorthologs OWNER TO agrbrdf;

