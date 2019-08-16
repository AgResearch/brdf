--
-- Name: gbskeyfilefact_backup25102016; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbskeyfilefact_backup25102016 (
    factid integer,
    biosampleob integer,
    flowcell character varying(32),
    lane integer,
    barcode character varying(32),
    sample character varying(32),
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
    createddate date,
    createdby character varying(256),
    voptypeid integer,
    control character varying(64),
    barcodedsampleob integer
);


ALTER TABLE public.gbskeyfilefact_backup25102016 OWNER TO agrbrdf;

--
-- Name: gbsyf_factidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE gbsyf_factidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gbsyf_factidseq OWNER TO agrbrdf;

