--
-- Name: checkaliquotrecord(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkaliquotrecord() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        units RECORD;
        terms RECORD;
    BEGIN
        if NEW.aliquotweightunit is not null then
           select into units  * from ontologytermfact where termname = NEW.aliquotweightunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.aliquotweightunit;
           end if;
        end if;

        if NEW.aliquotvolumeunit is not null then
           select into units  * from ontologytermfact where termname = NEW.aliquotvolumeunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.aliquotvolumeunit;
           end if;
        end if;

        if NEW.aliquotdmeunit is not null then
           select into units  * from ontologytermfact where termname = NEW.aliquotdmeunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.aliquotdmeunit;
           end if;
        end if;

        return NEW;
    END;
$$;


ALTER FUNCTION public.checkaliquotrecord() OWNER TO agrbrdf;

