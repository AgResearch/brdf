--
-- Name: data_set_2_r_results_180908; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE data_set_2_r_results_180908 (
    gene_id character varying(20),
    id__r integer,
    gene_name character varying(20),
    log_ratio double precision,
    absolute_log_ratio double precision,
    intensity double precision,
    fold_change double precision,
    biological_fold_change double precision,
    absolute_biological_fold_change double precision,
    raw_intensity double precision,
    simple_p_value double precision,
    moderated_p_value double precision,
    fdr double precision,
    log_mod_p_ double precision,
    log_fdr_ double precision,
    odds double precision,
    detail_scan_rank integer,
    no_dye_effect_fitted_scan_rank integer,
    no__good_spots integer,
    filter character varying(10),
    scan character varying(10),
    datasourceob integer,
    voptypeid integer,
    dataset character varying(20)
);


ALTER TABLE public.data_set_2_r_results_180908 OWNER TO agrbrdf;

