--
-- Name: optypesignature; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE optypesignature (
    obtypeid integer NOT NULL,
    argobtypeid integer NOT NULL,
    optablecolumn character varying(128)
);


ALTER TABLE public.optypesignature OWNER TO agrbrdf;

