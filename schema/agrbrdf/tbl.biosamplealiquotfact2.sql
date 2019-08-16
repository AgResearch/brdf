--
-- Name: biosamplealiquotfact2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplealiquotfact2 (
    biosamplealiquotfact integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096)
);


ALTER TABLE public.biosamplealiquotfact2 OWNER TO agrbrdf;

