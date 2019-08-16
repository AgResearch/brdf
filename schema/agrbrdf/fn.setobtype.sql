--
-- Name: setobtype(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION setobtype() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        NEW.obtypeid = TG_ARGV[0];
        NEW.createddate = now();
        RETURN NEW;
    END;
$$;


ALTER FUNCTION public.setobtype() OWNER TO agrbrdf;

