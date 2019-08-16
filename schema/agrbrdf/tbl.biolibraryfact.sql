--
-- Name: biolibraryfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biolibraryfact (
    biolibraryob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biolibraryfact OWNER TO agrbrdf;

