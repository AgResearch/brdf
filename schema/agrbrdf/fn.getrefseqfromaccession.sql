--
-- Name: getrefseqfromaccession(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getrefseqfromaccession(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   argseq alias for $1;
   reftype alias for $2;
   refseqcur refcursor;
   refresult varchar;
   arggeneid integer;
begin
   refresult := null;
   arggeneid := null;
   select getGeneidFromAccession(argseq,20) into arggeneid;
   if arggeneid is null then
      return argseq;
   else
      if reftype = 'mRNA' then
         open refseqcur for 
         select rna_nucleotide_accession from gene2accession where
         geneid = arggeneid and rna_nucleotide_accession like 'NM%';
      elsif reftype = 'protein' then
         open refseqcur for 
         select protein_accession from gene2accession where
         geneid = arggeneid and protein_accession like 'NP%';
      end if;

      fetch refseqcur into refresult;
      close refseqcur;

      if refresult is null then
         refresult := argseq;
      end if;

   end if;

   return refresult;

end;$_$;


ALTER FUNCTION public.getrefseqfromaccession(character varying, character varying) OWNER TO agrbrdf;

