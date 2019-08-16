--
-- Name: getattributefromaccession(character varying, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getattributefromaccession(character varying, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   locatorcur refcursor;
   argaccession0 alias for $1;
   maxversion alias for $2;
   attributename alias for $3;
   geneidres integer;
   tax_idres integer;
   argaccession varchar(64);
   tryaccession varchar(64);
   tryversion integer;
begin
   geneidres := null;

   if argaccession0 is null then
      return null;
   end if;

   argaccession := ltrim(rtrim(argaccession0));

--return errorMessage;

   -- first check format of input - check not too many dots
   if length(argaccession) - length(replace(argaccession,'.','')) > 1 then
      raise exception 'Bad accession format in argument ';
   end if;

   for tryversion in 0..maxVersion loop
      if tryversion > 0 then
         -- dePipe handles cases like ref|NM_blah| that often end up in our database
         tryaccession := dePipe(upper(split_part(argaccession,'.',1) || '.' || ltrim(rtrim(to_char(tryVersion,'9999')))));
         --raise notice '%' , tryaccession;
      else
         tryaccession := dePipe(upper(argaccession));
      end if;

      -- try each accession type - i.e. RNA,protein,Genomic.
      begin
         open locatorcur for
         select
            geneid,
            tax_id
         from
            gene2accession
         where
            rna_nucleotide_accession = tryaccession;
         fetch locatorcur into geneidres, tax_idres;
      exception
         when others then -- should be when no_data but this exception not known for some reason
         null;
      end;
      close locatorcur ;
      exit when geneidres is not null;


      begin
         open locatorcur for
         select
            geneid, 
            tax_id
         from
            gene2accession
         where
            protein_accession = tryaccession;
         fetch locatorcur into geneidres, tax_idres;
      exception
         when others then
         null;
      end;
      close locatorcur ;
      exit when geneidres is not null;

   end loop; -- try the argaccession, and if no hit, then try all versions of it


   if attributename = 'geneid' then
      return geneidres;
   else
      return tax_idres;
   end if;

end;$_$;


ALTER FUNCTION public.getattributefromaccession(character varying, integer, character varying) OWNER TO agrbrdf;

