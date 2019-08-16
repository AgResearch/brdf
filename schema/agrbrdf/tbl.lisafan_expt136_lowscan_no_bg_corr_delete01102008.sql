--
-- Name: lisafan_expt136_lowscan_no_bg_corr_delete01102008; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE lisafan_expt136_lowscan_no_bg_corr_delete01102008 (
    recnum integer,
    gene_name character varying(64),
    gene_id character varying(64),
    log_ratio double precision,
    absolute_log_ratio double precision,
    intensity double precision,
    fold_change double precision,
    biological_fold_change double precision,
    absolute_biological_fold_change double precision,
    raw_intensity double precision,
    simple_pvalue double precision,
    moderated_pvalue double precision,
    fdr double precision,
    log_mod_p double precision,
    log_fdr double precision,
    odds double precision,
    detail_scan_rank integer,
    high_scans_no_bg_corr_scan_rank integer,
    high_scans_normexp_scan_rank integer,
    low_scans_no_bg_corr_scan_rank integer,
    num_good_spots integer,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.lisafan_expt136_lowscan_no_bg_corr_delete01102008 OWNER TO agrbrdf;

