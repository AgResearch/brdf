--
-- Name: getrefseqfromgeneid(integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getrefseqfromgeneid(integer, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   arggeneid alias for $1;
   reftype alias for $2;
   refseqcur refcursor;
   refresult varchar;
begin
   refresult := null;
   if arggeneid is null then
      return null;
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


ALTER FUNCTION public.getrefseqfromgeneid(integer, character varying) OWNER TO agrbrdf;

--
-- Name: getrefseqfromgeneid(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getrefseqfromgeneid(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   arggeneid alias for $1;
   reftype alias for $2;
   refseqcur refcursor;
   refresult varchar;
begin
   refresult := null;
   if arggeneid is null then
      return null;
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

   end if;

   return refresult;

end;$_$;


ALTER FUNCTION public.getrefseqfromgeneid(character varying, character varying) OWNER TO agrbrdf;

