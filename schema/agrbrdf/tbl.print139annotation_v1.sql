--
-- Name: print139annotation_v1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE print139annotation_v1 (
    arraygene_name character varying(20),
    estname character varying(30),
    spotlsid character varying(40),
    contig character varying(30),
    tissue_expression character varying(260),
    humanovermouseoverrat_gene_id character varying(10),
    gene_taxid character varying(10),
    gene_symbol character varying(30),
    symbol_accession_for_ingenuity character varying(50),
    synonyms character varying(130),
    accession_chromosome character varying(20),
    map_location character varying(40),
    gene_description character varying(260),
    type_of_gene character varying(20),
    eof integer,
    datasourceob integer,
    voptypeid integer,
    oarchromosome character varying(32),
    contentid character varying(128)
);


ALTER TABLE public.print139annotation_v1 OWNER TO agrbrdf;

