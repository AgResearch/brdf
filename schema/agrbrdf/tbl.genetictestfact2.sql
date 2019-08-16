--
-- Name: genetictestfact2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genetictestfact2 (
    genetictestfact integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.genetictestfact2 OWNER TO agrbrdf;

