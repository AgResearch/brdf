--
-- Name: agg_newline_concat(text); Type: AGGREGATE; Schema: public; Owner: agrbrdf
--

CREATE AGGREGATE agg_newline_concat(text) (
    SFUNC = newline_concat,
    STYPE = text,
    INITCOND = ''
);


ALTER AGGREGATE public.agg_newline_concat(text) OWNER TO agrbrdf;

