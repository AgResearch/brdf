--
-- Name: keyfile_temp_nofastq; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE keyfile_temp_nofastq (
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
    bifo character varying(256)
);


ALTER TABLE public.keyfile_temp_nofastq OWNER TO agrbrdf;

