--
-- Name: gbskeyfilefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbskeyfilefact (
    factid integer DEFAULT nextval('keyfile_factidseq'::regclass) NOT NULL,
    biosampleob integer NOT NULL,
    flowcell character varying(32),
    lane integer,
    barcode character varying(32),
    sample character varying(64),
    platename character varying(32),
    platerow character varying(32),
    platecolumn integer,
    libraryprepid integer,
    counter integer,
    comment character varying(256),
    enzyme character varying(32),
    species character varying(256),
    numberofbarcodes character varying(4),
    bifo character varying(256),
    fastq_link character varying(256),
    createddate date DEFAULT now(),
    createdby character varying(256),
    voptypeid integer,
    control character varying(64),
    barcodedsampleob integer,
    subjectname character varying(64),
    windowsize character varying(32),
    gbs_cohort character varying(64),
    qc_cohort character varying(128),
    qc_sampleid character varying(32),
    refgenome_bwa_indexes character varying(1024),
    refgenome_blast_indexes character varying(1024),
    biosubjectob integer
);


ALTER TABLE public.gbskeyfilefact OWNER TO agrbrdf;

