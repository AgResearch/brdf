--
-- Name: biosamplingfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplingfact (
    biosamplingfunction integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096),
    unitname character varying(256)
);


ALTER TABLE public.biosamplingfact OWNER TO agrbrdf;

