--
-- Name: genotypestudyfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypestudyfact (
    genotypestudy integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.genotypestudyfact OWNER TO agrbrdf;

