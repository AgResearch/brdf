--
-- Name: lindawheat1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE lindawheat1 (
    id__r integer,
    gene_id character varying(30),
    log_ratio double precision,
    biological_fold_change double precision,
    moderated_p_value double precision,
    fdr double precision,
    flag1 integer,
    flag2 integer,
    log_ratio_1 double precision,
    fold_change double precision,
    biological_fold_change_1 double precision,
    absolute_biol_fold_change double precision,
    geomean_1 double precision,
    geomean_2 double precision,
    maximum_geomean double precision,
    simple_p_value double precision,
    moderated_p_value_1 double precision,
    fdr_1 double precision,
    logmod_p double precision,
    logfdr double precision,
    flag1_1 integer,
    flag2_1 integer,
    df_resid double precision,
    df_total double precision,
    scan_rank integer,
    pma_call__lj0001_wheat_cel character varying(10),
    pma_call__lj0002_wheat_cel character varying(10),
    pma_call__lj0003_wheat_cel character varying(10),
    pma_call__lj0004_wheat_cel character varying(10),
    pma_call__lj0005_wheat_cel character varying(10),
    pma_call__lj0006_wheat_cel character varying(10),
    genechip_array character varying(20),
    species_scientific_name character varying(20),
    annotation_date character varying(20),
    sequence_type character varying(20),
    sequence_source character varying(10),
    transcript_idarray_design character varying(20),
    target_description character varying(340),
    representative_public_id character varying(20),
    archival_unigene_cluster character varying(10),
    unigene_id character varying(30),
    genome_version character varying(10),
    alignments character varying(10),
    gene_title character varying(110),
    gene_symbol character varying(10),
    chromosomal_location character varying(10),
    unigene_cluster_type character varying(20),
    ensembl character varying(10),
    entrez_gene character varying(10),
    swissprot character varying(10),
    ec character varying(10),
    omim character varying(10),
    refseq_protein_id character varying(10),
    refseq_transcript_id character varying(10),
    flybase character varying(10),
    agi character varying(10),
    wormbase character varying(10),
    mgi_name character varying(10),
    rgd_name character varying(10),
    sgd_accession_number character varying(10),
    gene_ontology_biological_process character varying(10),
    gene_ontology_cellular_component character varying(80),
    gene_ontology_molecular_function character varying(70),
    pathway character varying(10),
    interpro character varying(10),
    trans_membrane character varying(50),
    qtl character varying(10),
    annotation_description character varying(180),
    annotation_transcript_cluster character varying(210),
    transcript_assignments character varying(2070),
    annotation_notes character varying(510),
    input_probe_set character varying(30),
    probe_set_name_found character varying(30),
    exemplar_assembly character varying(10),
    exemplar_unigene character varying(20),
    pre_polya_trim_length integer,
    members integer,
    num__unigenes integer,
    unigenes_represented character varying(40),
    uniprot_accn character varying(30),
    uniprot_e_score double precision,
    uniprot_desc character varying(170),
    rice_accn character varying(20),
    rice_e_score double precision,
    rice_chr integer,
    rice_5prime integer,
    rice_3prime integer,
    rice_desc character varying(100),
    arab_accn character varying(20),
    arab_e_score double precision,
    arab_chr integer,
    arab_5prime integer,
    arab_3prime integer,
    arab_desc character varying(140),
    heatmap_order_relative_to_data_sorted_by_transcript_id integer
);


ALTER TABLE public.lindawheat1 OWNER TO agrbrdf;
