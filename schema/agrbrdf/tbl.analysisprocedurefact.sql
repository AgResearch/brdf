--
-- Name: analysisprocedurefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE analysisprocedurefact (
    analysisprocedureob integer NOT NULL,
    factnamespace character varying(256),
    attributedate date,
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.analysisprocedurefact OWNER TO agrbrdf;

