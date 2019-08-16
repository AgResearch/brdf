--
-- Name: taxonomy_names; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE taxonomy_names (
    tax_id integer,
    name_txt character varying(1024),
    unique_name character varying(1024),
    name_class character varying(1024),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.taxonomy_names OWNER TO agrbrdf;

