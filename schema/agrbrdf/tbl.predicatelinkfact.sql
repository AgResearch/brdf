--
-- Name: predicatelinkfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE predicatelinkfact (
    predicatelink integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.predicatelinkfact OWNER TO agrbrdf;

