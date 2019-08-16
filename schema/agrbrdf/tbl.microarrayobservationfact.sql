--
-- Name: microarrayobservationfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE microarrayobservationfact (
    microarrayobservation integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.microarrayobservationfact OWNER TO agrbrdf;

