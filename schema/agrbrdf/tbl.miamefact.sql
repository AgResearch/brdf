--
-- Name: miamefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE miamefact (
    microarraystudy integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.miamefact OWNER TO agrbrdf;

