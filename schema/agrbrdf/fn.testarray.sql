--
-- Name: testarray(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION testarray() RETURNS integer
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms integer[];
    BEGIN
        terms[3]=4;
        return terms[3];
    END;
$$;


ALTER FUNCTION public.testarray() OWNER TO agrbrdf;

