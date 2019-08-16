--
-- Name: filterkeywords(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION filterkeywords() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select lower(NEW.obkeywords) into NEW.obkeywords;
        return NEW;
    END;
$$;


ALTER FUNCTION public.filterkeywords() OWNER TO agrbrdf;

