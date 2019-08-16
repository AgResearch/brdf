--
-- Name: from_hex(text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION from_hex(t text) RETURNS integer
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $$
  DECLARE
    r RECORD;
  BEGIN
    FOR r IN EXECUTE 'SELECT x'''||t||'''::integer AS hex' LOOP
      RETURN r.hex;
    END LOOP;
  END
$$;


ALTER FUNCTION public.from_hex(t text) OWNER TO agrbrdf;

