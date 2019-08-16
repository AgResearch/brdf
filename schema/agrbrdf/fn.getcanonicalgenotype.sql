--
-- Name: getcanonicalgenotype(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getcanonicalgenotype(character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   rawarggenotype alias for $1;
   arggenotype varchar(32);
   allele1 varchar(32);
   allele2 varchar(32);
   canonicalgenotype varchar(32);
begin
   arggenotype = trim(rawarggenotype);  
   canonicalgenotype := '??';

   if (arggenotype not like '%?%') and (upper(arggenotype) not like '%UNKNOWN%')  then
      allele1 = substr(arggenotype, 1, 1);
      allele2 = substr(arggenotype, 2, 1);
      if allele1 is not null and allele2 is not null then
         if length(allele1) > 0 and length(allele2) > 0 then
            if allele1 <= allele2 then
               canonicalgenotype := upper(allele1 || allele2);
            else
               canonicalgenotype := upper(allele2 || allele1);
            end if;
         end if;
      end if;
   end if;
   return canonicalgenotype;
end;
$_$;


ALTER FUNCTION public.getcanonicalgenotype(character varying) OWNER TO agrbrdf;

--
-- Name: FUNCTION getcanonicalgenotype(character varying); Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON FUNCTION getcanonicalgenotype(character varying) IS 'This function tidies up the raw genotype and returns in a canonical format. E.G. GC becomes CG ; ?T becomes ?? etc';


