--
-- Name: geosubmissiondata; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geosubmissiondata (
    recnum integer,
    sourcefile character varying(128),
    id_ref integer,
    gene_name character varying(64),
    spot_id character varying(64),
    value double precision,
    ch1_sig_mean double precision,
    ch1_bkd_mean double precision,
    ch2_sig_mean double precision,
    ch2_bkd_mean double precision,
    datasourceob integer,
    voptypeid integer,
    poolid1 character varying(32),
    genesymbol character varying(30),
    norm_intensity double precision,
    filerecnum integer,
    control_type integer,
    gisfeatnonunifol integer,
    risfeatpopnol integer,
    risfeatnonunifol integer,
    gisfeatpopnol integer
);


ALTER TABLE public.geosubmissiondata OWNER TO agrbrdf;

