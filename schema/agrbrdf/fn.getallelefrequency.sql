--
-- Name: getallelefrequency(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getallelefrequency(integer, character varying, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   SNPid alias for $1;
   animalClass alias for $2;
   allelearg alias for $3;
   cursGenotype refcursor;
   GenotypeToProcess character varying (2);

   alleleCount integer;

begin
  --open query to get all classes we want to summarise   

    OPEN cursGenotype FOR
	SELECT
          getCanonicalGenotype(gto.genotypeobserved) as genotype
        from
          (((oblist o join listmembershiplink l on 
             o.xreflsid = animalClass  and
             l.oblist = o.obid) join
             biosamplingfunction b on b.biosubjectob = l.ob) join
             genotypestudy g on g.biosampleob = b.biosampleob) join
             genotypeobservation gto on gto.genotypestudy = g.obid and
             gto.genetictestfact = SNPid;

    alleleCount := 0;
    LOOP
      FETCH cursGenotype into GenotypeToProcess;

      IF NOT FOUND THEN
        EXIT;
      END IF;


      IF GenotypeToProcess = '??' and (upper(allelearg) = 'UNKNOWN' or allelearg = '??') THEN
        alleleCount := alleleCount + 2;
      ELSE
        IF upper(SUBSTR(GenotypeToProcess,1,1)) = upper(allelearg) THEN
	  alleleCount := alleleCount + 1;
        END IF;

        IF upper(SUBSTR(GenotypeToProcess,2,1)) = upper(allelearg) THEN
	  alleleCount := alleleCount + 1;
        END IF;
      END IF;
    END LOOP;

    CLOSE cursGenotype;
    -- write accumulated stats to table

  RETURN   alleleCount; 
end;
$_$;


ALTER FUNCTION public.getallelefrequency(integer, character varying, character varying) OWNER TO agrbrdf;

