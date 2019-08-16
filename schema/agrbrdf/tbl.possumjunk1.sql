--
-- Name: possumjunk1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE possumjunk1 (
    besthit character varying(64),
    tax_id integer,
    geneid character varying(32),
    symbol character varying(64),
    locustag character varying(64),
    synonyms character varying(2048),
    chromosome character varying(64),
    map_location character varying(64),
    description character varying(256),
    type_of_gene character varying(64)
);


ALTER TABLE public.possumjunk1 OWNER TO agrbrdf;

