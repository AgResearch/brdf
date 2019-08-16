--
-- Name: reproductionmicroarrayplasmids; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE reproductionmicroarrayplasmids (
    microarray_code character varying(10),
    plasmid_id character varying(10),
    vector_id character varying(20),
    species character varying(10),
    gene character varying(20),
    geneid character varying(10),
    gene_name character varying(80),
    size_bp character varying(10),
    primer_pairs character varying(10),
    dna_concentration character varying(20),
    conc_in_ngoverul character varying(20),
    dilute_by_to_get_50_ngoverul character varying(10),
    sample_ul character varying(10),
    water_ul character varying(10),
    col character varying(10),
    col_1 integer,
    microarray_code_1 character varying(10),
    plasmid_id_1 character varying(10),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.reproductionmicroarrayplasmids OWNER TO agrbrdf;

