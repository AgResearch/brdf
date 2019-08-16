--
-- Name: checkworkflowontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkworkflowontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.workFlowStageType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'WORKFLOW_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid workflow stage type ', NEW.workFlowStageType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkworkflowontology() OWNER TO agrbrdf;

