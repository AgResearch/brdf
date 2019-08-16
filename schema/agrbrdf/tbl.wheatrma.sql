--
-- Name: wheatrma; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE wheatrma (
    gene character varying(30),
    uninfected_1 double precision,
    uninfected_2 double precision,
    uninfected_3 double precision,
    infected_1 double precision,
    infected_2 double precision,
    infected_3 double precision,
    datasourceob integer,
    voptypeid integer,
    fileorder integer
);


ALTER TABLE public.wheatrma OWNER TO agrbrdf;

