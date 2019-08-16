--
-- Name: checkdatasourceontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkdatasourceontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.dataSourceType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'DATASOURCE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid datasource type ', NEW.dataSourceType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkdatasourceontology() OWNER TO agrbrdf;

