--
-- Name: checksecurityfunctionobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checksecurityfunctionobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        if NEW.ob is not null then
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'checksecurityfunctionobkey : key error - obid not found';
        end if;
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checksecurityfunctionobkey() OWNER TO agrbrdf;

