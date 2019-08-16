--
-- Name: checkcommentedobkey(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkcommentedobkey() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        if NEW.commentedOb is not null then
           select obid into NEW.commentedOb from ob where obid = NEW.commentedOb;
           if not FOUND then
              RAISE EXCEPTION 'key error - commentedOb not found';
           end if;
        end if;
        return NEW;
    END;
$$;


ALTER FUNCTION public.checkcommentedobkey() OWNER TO agrbrdf;

