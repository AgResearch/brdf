--
-- Name: checkdisplayfunctionobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkdisplayfunctionobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'checkdisplayfunctionobkey : key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkdisplayfunctionobkey() OWNER TO agrbrdf;

