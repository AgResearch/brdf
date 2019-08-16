--
-- Name: hg18_refgenes_location; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_refgenes_location (
    name character varying(20),
    chrom character varying(20),
    strand character varying(10),
    transcriptionstart integer,
    transcriptionend integer,
    cdsstart integer,
    cdsend integer,
    id integer,
    name2 character varying(30),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.hg18_refgenes_location OWNER TO agrbrdf;

