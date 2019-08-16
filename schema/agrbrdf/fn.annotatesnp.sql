--
-- Name: annotatesnp(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION annotatesnp(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   SNPid alias for $1;
   annotationtype alias for $2;
   animalClass alias for $3;
 
   cursClasses refcursor;
   ClassToSummarise character varying (2048);

   cursGenotype refcursor;
   GenotypeToProcess character varying (2);

   alleleCountA int4;
   alleleCountC int4;
   alleleCountG int4;
   alleleCountT int4;
   alleleCountUnknown int4;
   alleleCountTotal int4;

  testoutput character varying (200);
begin
  --open query to get all classes we want to summarise   

  OPEN cursClasses FOR 
	SELECT xreflsid
	from 
	  oblist
	where
	  xreflsid like animalClass;
  LOOP
    FETCH cursClasses into ClassToSummarise;

    IF NOT FOUND THEN
      EXIT;
    END IF;

 -- for each class
   -- open query to return all genotypes for this SNP for all animals in class, 
   -- for the SNPid passed in as an arg to the function

    alleleCountA = 0;
    alleleCountC = 0;
    alleleCountG = 0;
    alleleCountT = 0;
    alleleCountUnknown = 0;
    alleleCountTotal = 0;

    OPEN cursGenotype FOR
	SELECT
          getCanonicalGenotype(gto.genotypeobserved) as genotype
        from
          (((oblist o join listmembershiplink l on 
             o.xreflsid = ClassToSummarise  and
             l.oblist = o.obid) join
             biosamplingfunction b on b.biosubjectob = l.ob) join
             genotypestudy g on g.biosampleob = b.biosampleob) join
             genotypeobservation gto on gto.genotypestudy = g.obid and
             gto.genetictestfact = SNPid;

    LOOP
      FETCH cursGenotype into GenotypeToProcess;

      IF NOT FOUND THEN
        EXIT;
      END IF;

      -- for each record
      -- accumulate stats
    
      alleleCountTotal = alleleCountTotal + 2; 

      IF SUBSTR(GenotypeToProcess,1,1) = 'A' THEN
	alleleCountA = alleleCountA + 1;
      END IF;

      IF SUBSTR(GenotypeToProcess,2,1) = 'A' THEN
	alleleCountA = alleleCountA + 1;
      END IF;
      
      IF SUBSTR(GenotypeToProcess,1,1) = 'C' THEN
	alleleCountC = alleleCountC + 1;
      END IF;
      IF SUBSTR(GenotypeToProcess,2,1) = 'C' THEN
	alleleCountC = alleleCountC + 1;
      END IF;
      
      IF SUBSTR(GenotypeToProcess,2,1) = 'G' THEN
	alleleCountG = alleleCountG + 1;
      END IF;
      IF SUBSTR(GenotypeToProcess,1,1) = 'G' THEN
	alleleCountG = alleleCountG + 1;
      END IF;
      
      IF SUBSTR(GenotypeToProcess,1,1) = 'T' THEN
	alleleCountT = alleleCountT + 1;
      END IF;
      IF SUBSTR(GenotypeToProcess,2,1) = 'T' THEN
	alleleCountT = alleleCountT + 1;
      END IF;
            
      IF GenotypeToProcess = '??' THEN
	alleleCountUnknown = alleleCountUnknown + 2;
      END IF;
  
    END LOOP;

    CLOSE cursGenotype;
    -- write accumulated stats to table

    IF alleleCountTotal > 0 THEN
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_A', alleleCountA);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_C', alleleCountC);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_G', alleleCountG);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_T', alleleCountT);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_Unknown', alleleCountUnknown);
       INSERT INTO genetictestfact2 (genetictestfact, factnamespace, attributename, attributevalue)
	  VALUES (SNPid, ClassToSummarise, 'AF_All', alleleCountTotal);

    END IF;

  END LOOP;
  CLOSE cursClasses;
  RETURN   'TRUE'; -- to_char(alleleCountT, '99999D99');  -- testoutput; 
end;
$_$;


ALTER FUNCTION public.annotatesnp(integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: FUNCTION annotatesnp(integer, character varying, character varying); Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON FUNCTION annotatesnp(integer, character varying, character varying) IS 'This function adds annotation (allele frequency etc) to the genetictestfact2 table';


