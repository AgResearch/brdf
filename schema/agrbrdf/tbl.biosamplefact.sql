--
-- Name: biosamplefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplefact (
    biosampleob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biosamplefact OWNER TO agrbrdf;

