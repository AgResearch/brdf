--
-- Name: datasourcefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE datasourcefact (
    datasourceob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.datasourcefact OWNER TO agrbrdf;

