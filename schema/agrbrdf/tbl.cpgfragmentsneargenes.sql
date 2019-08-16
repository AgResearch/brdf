--
-- Name: cpgfragmentsneargenes; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE cpgfragmentsneargenes (
    cpg_uniqueid character varying(30),
    frag_uniqueid character varying(30),
    refseq character varying(20),
    transcriptionstart integer,
    transcriptionend integer,
    strand character varying(10),
    name2 character varying(30),
    datasourceob integer,
    voptypeid integer,
    fragstart integer,
    fragstop integer
);


ALTER TABLE public.cpgfragmentsneargenes OWNER TO agrbrdf;

