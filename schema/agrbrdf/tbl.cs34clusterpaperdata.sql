--
-- Name: cs34clusterpaperdata; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE cs34clusterpaperdata (
    contig character varying(20),
    refseq character varying(20),
    gene_name character varying(20),
    blast_e_value character varying(20),
    gnf_atlas_2_data character varying(10),
    total_no__of_ests_in_contig integer,
    number_of_contigs_in_cluster integer,
    cluster_number integer,
    cluster_name character varying(20),
    datasourceob integer,
    voptypeid integer,
    contigname character varying(64)
);


ALTER TABLE public.cs34clusterpaperdata OWNER TO agrbrdf;

