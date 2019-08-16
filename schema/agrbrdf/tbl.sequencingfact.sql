--
-- Name: sequencingfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE sequencingfact (
    sequencingfunction integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.sequencingfact OWNER TO agrbrdf;

