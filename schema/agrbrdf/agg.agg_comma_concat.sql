--
-- Name: agg_comma_concat(text); Type: AGGREGATE; Schema: public; Owner: agrbrdf
--

CREATE AGGREGATE agg_comma_concat(text) (
    SFUNC = comma_concat,
    STYPE = text,
    INITCOND = ''
);


ALTER AGGREGATE public.agg_comma_concat(text) OWNER TO agrbrdf;

