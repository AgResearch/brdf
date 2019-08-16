--
-- Name: gene2accession; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gene2accession (
    tax_id integer,
    geneid character varying(128),
    status character varying(64),
    rna_nucleotide_accession character varying(64),
    rna_nucleotide_gi character varying(32),
    protein_accession character varying(64),
    protein_gi character varying(32),
    genomic_nucleotide_accession character varying(64),
    genomic_nucleotide_gi character varying(32),
    start_position_on_the_genomic_accession character varying(32),
    end_position_on_the_genomic_accession character varying(32),
    orientation character varying(8),
    assembly character varying(64),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.gene2accession OWNER TO agrbrdf;

