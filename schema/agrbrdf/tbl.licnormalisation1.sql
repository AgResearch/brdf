--
-- Name: licnormalisation1; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE licnormalisation1 (
    probeset character varying(30),
    lipid_pct double precision,
    crude_aa_pct double precision,
    true_aa_pct double precision,
    casein_pct double precision,
    lcts_pct double precision,
    ttl_solid_pct double precision,
    scc double precision,
    growth_hormone double precision,
    igf_1 double precision,
    insulin double precision,
    sire double precision,
    am_and_pm__average_milk_volume double precision,
    crude_aa_yield double precision,
    true_aa_yield double precision,
    casein_yield double precision,
    number_of_present_calls_over_all_254_slides integer,
    number_of_present_calls_for_just_the_tissue_samples character varying(10),
    analysisname character varying(32),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.licnormalisation1 OWNER TO agrbrdf;

