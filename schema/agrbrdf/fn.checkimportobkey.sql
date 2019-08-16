--
-- Name: checkimportobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkimportobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'checkimportobkey : key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkimportobkey() OWNER TO agrbrdf;

