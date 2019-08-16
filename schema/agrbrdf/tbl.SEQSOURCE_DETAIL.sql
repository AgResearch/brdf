--
-- Name: SEQSOURCE_DETAIL; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE "SEQSOURCE_DETAIL" (
    "SOURCECODE" character varying(50),
    "DETAIL_NAME" character varying(64),
    "DETAIL_VALUE" character varying(4000)
);


ALTER TABLE public."SEQSOURCE_DETAIL" OWNER TO agrbrdf;

