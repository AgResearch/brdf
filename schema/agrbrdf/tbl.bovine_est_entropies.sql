--
-- Name: bovine_est_entropies; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE bovine_est_entropies (
    estname character varying(20),
    btrefseq_agbovine_csv double precision,
    bgisheep_agbovine_csv double precision,
    bovinevelevetse_agbovine_csv double precision,
    btau42_agbovine_csv double precision,
    btau461_agbovine_csv double precision,
    cs34_agbovine_csv double precision,
    cs39_agbovine_csv double precision,
    dfcibt_agbovine_csv double precision,
    dfcioa_agbovine_csv double precision,
    umd2_agbovine_csv double precision,
    umd3_agbovine_csv double precision
);


ALTER TABLE public.bovine_est_entropies OWNER TO agrbrdf;

