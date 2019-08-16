--
-- Name: checksampleunits(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checksampleunits() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        units RECORD;
    BEGIN
        if NEW.sampleweightunit is not null then
           select into units  * from ontologytermfact where termname = NEW.sampleweightunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.sampleweightunit;
           end if;
        end if;

        if NEW.samplevolumeunit is not null then
           select into units  * from ontologytermfact where termname = NEW.samplevolumeunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.samplevolumeunit;
           end if;
        end if;

        if NEW.sampledmeunit is not null then
           select into units  * from ontologytermfact where termname = NEW.sampledmeunit and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.sampledmeunit;
           end if;
        end if;

        return NEW;
    END;
$$;


ALTER FUNCTION public.checksampleunits() OWNER TO agrbrdf;

