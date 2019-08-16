--
-- Name: microarrayobservation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE microarrayobservation (
    microarraystudy integer NOT NULL,
    microarrayspotfact integer,
    gpr_block integer,
    gpr_column integer,
    gpr_row integer,
    gpr_name character varying(256),
    gpr_id character varying(256),
    gpr_dye1foregroundmean integer,
    gpr_dye1backgroundmean integer,
    gpr_dye2foregroundmean integer,
    gpr_dye2backgroundmean integer,
    gpr_logratio real,
    gpr_flags integer,
    gpr_autoflag integer,
    norm_logratio real,
    norm_dye1intensity real,
    norm_dye2intensity real,
    rawdatarecord text,
    observationcomment character varying(1024),
    affy_meanpm double precision,
    affy_meanmm double precision,
    affy_stddevpm double precision,
    affy_stddevmm double precision,
    affy_count integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 250))
)
INHERITS (op);


ALTER TABLE public.microarrayobservation OWNER TO agrbrdf;

