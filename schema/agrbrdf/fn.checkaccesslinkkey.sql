--
-- Name: checkaccesslinkkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkaccesslinkkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        select obid into NEW.ob from ob where obid = NEW.ob;
        if not FOUND then
           RAISE EXCEPTION 'key error - obid not found';
        end if;

        --the list should have type USR ROLE
        if oblist is not null then
        end if;



        return NEW;
    END;
$$;


ALTER FUNCTION public.checkaccesslinkkey() OWNER TO agrbrdf;

