--
-- Name: agg_comment_concat(text); Type: AGGREGATE; Schema: public; Owner: agrbrdf
--

CREATE AGGREGATE agg_comment_concat(text) (
    SFUNC = comment_concat,
    STYPE = text,
    INITCOND = ''
);


ALTER AGGREGATE public.agg_comment_concat(text) OWNER TO agrbrdf;

