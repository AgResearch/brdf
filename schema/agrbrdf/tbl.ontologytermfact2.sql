--
-- Name: ontologytermfact2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ontologytermfact2 (
    ontologytermid integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.ontologytermfact2 OWNER TO agrbrdf;

