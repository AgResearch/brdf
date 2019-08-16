--
-- Name: geneexpressionstudyfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneexpressionstudyfact (
    geneexpressionstudy integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.geneexpressionstudyfact OWNER TO agrbrdf;

