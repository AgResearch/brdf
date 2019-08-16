--
-- Name: checkcommentlinkkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkcommentlinkkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'key error - obid not found';
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkcommentlinkkey() OWNER TO agrbrdf;

