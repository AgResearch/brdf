--
-- Name: accesslink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE accesslink (
    ob integer NOT NULL,
    staffob integer,
    oblist integer,
    accesstype character varying(64),
    accesscomment text,
    createddate date DEFAULT now(),
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256)
);


ALTER TABLE public.accesslink OWNER TO agrbrdf;

