--
-- Name: librarysequencingfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE librarysequencingfact (
    librarysequencingfunction integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.librarysequencingfact OWNER TO agrbrdf;

