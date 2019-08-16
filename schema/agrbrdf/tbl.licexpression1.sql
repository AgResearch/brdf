--
-- Name: licexpression1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE licexpression1 (
    anml_key integer,
    inputfile character varying(64),
    affygene character varying(64),
    expression double precision,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.licexpression1 OWNER TO agrbrdf;

