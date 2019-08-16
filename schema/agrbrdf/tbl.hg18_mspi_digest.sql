--
-- Name: hg18_mspi_digest; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_mspi_digest (
    chrom character varying(10),
    accession character varying(40),
    start integer,
    stop integer,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.hg18_mspi_digest OWNER TO agrbrdf;

