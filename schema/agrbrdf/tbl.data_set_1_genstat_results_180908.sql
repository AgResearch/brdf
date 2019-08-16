--
-- Name: data_set_1_genstat_results_180908; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE data_set_1_genstat_results_180908 (
    probes character varying(20),
    intensity double precision,
    est_1_ double precision,
    est_2_ double precision,
    est_3_ double precision,
    df integer,
    res_sd double precision,
    dbias double precision,
    se_1_ double precision,
    se_2_ double precision,
    se_3_ double precision,
    tval_1_ double precision,
    tval_2_ double precision,
    tval_3_ double precision,
    prob_1_ double precision,
    prob_2_ double precision,
    prob_3_ double precision,
    cont1ghvc double precision,
    cont2atrvc double precision,
    cont3atrvgh double precision,
    secont_1_ double precision,
    secont_2_ double precision,
    secont_3_ double precision,
    ctval_1_ double precision,
    ctval_2_ double precision,
    ctval_3_ double precision,
    cprob_1_ double precision,
    cprob_2_ double precision,
    cprob_3_ double precision,
    mod_sd double precision,
    mtval_1_ double precision,
    mtval_2_ double precision,
    mtval_3_ double precision,
    mcprob_1_ double precision,
    mcprob_2_ double precision,
    mcprob_3_ double precision,
    gene_id character varying(20),
    foldgh1 double precision,
    foldat1 double precision,
    foldgh2 double precision,
    foldat2 double precision,
    voptypeid integer,
    datasourceob integer,
    dataset character varying(20),
    fold double precision,
    prob double precision,
    intens double precision
);


ALTER TABLE public.data_set_1_genstat_results_180908 OWNER TO agrbrdf;

