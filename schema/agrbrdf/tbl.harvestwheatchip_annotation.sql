--
-- Name: harvestwheatchip_annotation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE harvestwheatchip_annotation (
    all_probes character varying(30),
    probe_set_name_found character varying(30),
    exemplar_assembly character varying(10),
    exemplar_unigene character varying(20),
    pre_polya_trim_length integer,
    members integer,
    num__unigenes integer,
    unigenes_represented character varying(910),
    uniprot_accn character varying(30),
    uniprot_e_score double precision,
    uniprot_desc character varying(170),
    rice_accn character varying(20),
    rice_e_score double precision,
    rice_chr integer,
    rice_5prime integer,
    rice_3prime integer,
    rice_desc character varying(130),
    arab_accn character varying(20),
    arab_e_score double precision,
    arab_chr character varying(10),
    arab_5prime integer,
    arab_3prime integer,
    arab_desc character varying(140),
    brachy_accn character varying(20),
    brachy_e_score double precision,
    brachy_chr character varying(10),
    brachy_5prime integer,
    brachy_3prime integer,
    brachy_desc character varying(90),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.harvestwheatchip_annotation OWNER TO agrbrdf;

