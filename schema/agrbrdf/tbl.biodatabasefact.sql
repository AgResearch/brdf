--
-- Name: biodatabasefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biodatabasefact (
    biodatabaseob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue text
);


ALTER TABLE public.biodatabasefact OWNER TO agrbrdf;

