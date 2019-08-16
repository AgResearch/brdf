--
-- Name: checkpredicatekeys(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkpredicatekeys() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select a.obid , b.obid into NEW.subjectob,NEW.objectob from ob a, ob b  where a.obid = NEW.subjectob and b.obid = NEW.objectob;
        if not FOUND then
           RAISE EXCEPTION 'key error - subject or object obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkpredicatekeys() OWNER TO agrbrdf;

