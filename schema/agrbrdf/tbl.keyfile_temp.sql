--
-- Name: keyfile_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE keyfile_temp (
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
    control character varying(64),
    windowsize character varying(32),
    gbs_cohort character varying(32)
);


ALTER TABLE public.keyfile_temp OWNER TO agrbrdf;

