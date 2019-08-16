--
-- Name: accessfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE accessfact (
    ob integer NOT NULL,
    accesstype character varying(64),
    accesscomment text,
    createddate date DEFAULT now(),
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256)
);


ALTER TABLE public.accessfact OWNER TO agrbrdf;

