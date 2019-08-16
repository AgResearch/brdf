--
-- Name: checkvoptypeid(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkvoptypeid() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        if NEW.voptypeid is not null then
           select obtypeid into NEW.voptypeid from obtype where obtypeid = NEW.voptypeid and isop ;
           if not FOUND then
              RAISE EXCEPTION 'key error - voptypeid to insert is not a valid op type ';
           end if;
        end if;

        return NEW;
    END;
$$;


ALTER FUNCTION public.checkvoptypeid() OWNER TO agrbrdf;

