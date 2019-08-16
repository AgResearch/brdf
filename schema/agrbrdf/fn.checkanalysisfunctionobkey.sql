--
-- Name: checkanalysisfunctionobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkanalysisfunctionobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'checkanalysisfunctionobkey : key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkanalysisfunctionobkey() OWNER TO agrbrdf;

