--
-- Name: getgenbankrecord(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgenbankrecord(character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
DECLARE
   cursr refcursor;
   speciesVal varchar;
   taxidVal varchar;
   source varchar;
   
   seqname varchar;
   seqtypeholder varchar;
   seqlen integer;
   seqstr varchar;
   seqtype varchar;
   seqtop varchar;
   seqdate date;

   feattype varchar;
   featstart integer;
   featstop integer;
   featxref varchar;
   featcom varchar;
   featevid varchar;

   --biosequenceobid ALIAS for $1;
   biosequenceobid integer;
   seqbuff varchar;
   strbuff varchar;

   comments varchar;
   position integer;
   basesize integer;
   lastfeature varchar;
   lastseqstart integer;
   lastseqstop integer;

BEGIN
   --Test if obid is an obid or is an xreflsid
   select into biosequenceobid obid from biosequenceob where xreflsid = $1;
   if not FOUND then
      select into biosequenceobid obid from biosequenceob where obid = $1;
   end if;
   if not FOUND then
      return 'ERROR - obid not found!';
   end if;
   
   strbuff := '';

   open cursr for
    select
       sequencename,    --name                                 seqname
       seqlength,       --number of bps or aas               seqlen
       seqstring,       --dna/aa sequence                      seqstr
       sequencetype,    --type of sequence, eg "genomic DNA"   seqtype
       sequencetopology,--type of sequence, eg "genomic DNA"   seqtop
       createddate      --date record was created              seqdate
    from
       biosequenceob
    where
       obid = biosequenceobid;
    
   fetch cursr into seqname, seqlen, seqstr, seqtype, seqtop, seqdate;

   close cursr;
   
   if (strpos(seqtype,'RNA') > 0) then
      seqtypeholder = ' bp    RNA';
   elsif (strpos(seqtype,'DNA') > 0) then
      seqtypeholder = ' bp    DNA';
   elsif (strpos(seqtype,'PROTEIN') > 0) then
      seqtypeholder = ' aa       ';
   else
      seqtypeholder = '          ';
   end if;

   -- LOCUS       <externalname>
   if (length(seqname)<25) then
      seqbuff := 'LOCUS       '||rpad(seqname, 25, ' ');
   else 
      seqbuff := 'LOCUS       '||seqname||' ';
   end if;
   strbuff := strbuff||seqbuff;
   
   seqbuff := seqlen||
        seqtypeholder||'     '||
        seqtop||'   '||
        '    '|| --MAM, INV, etc (the genus? e.g. Mammal, Invertebrate - is this recorded?)
        to_char(seqdate, 'DD-MON-YYYY')||chr(10);
   strbuff := strbuff||seqbuff;

   -- ACCESSION   <externalname>
   seqbuff := 'ACCESSION   '||seqname||chr(10);
   strbuff := strbuff||seqbuff;

    -- SOURCE      AgResearch
   select into source su.subjectspeciesname 
   from biosubjectob su, biosamplingfunction f, biosampleob sa, sequencingfunction se
   where su.obid = f.biosubjectob
   and f.biosampleob = sa.obid
   and sa.obid = se.biosampleob
   and se.biosequenceob = biosequenceobid;
   
   if FOUND then 
      seqbuff := 'SOURCE      '||source||chr(10);
      strbuff := strbuff||seqbuff;
   end if;
    
   open cursr for
    select
       speciesname, --speciesVal
       speciestaxid --taxidVal
    from
       geneticlocationfact 
    where
       biosequenceob = biosequenceobid
       and speciestaxid is not null;

   fetch cursr into speciesVal, taxidVal;

   close cursr;
   
   if NOT FOUND then --is this right? Will it do what I want???
      speciesVal := '';
      taxidVal := '';
   end if;

   -- TAXON (Source Organism)
   if speciesVal != '' then
      seqbuff := '  ORGANISM  '||speciesVal||chr(10);
      strbuff := strbuff||seqbuff;
   end if;

   open cursr for
     select
        featuretype,    --feature title  feattype
        featurestart,   --start pos      featstart
        featurestop,    --stop pos       featstop
        xreflsid,       --/db_xref=      featxref
        featurecomment, --/note=         featcom
        evidence        --/evidence=     featevid
     from
        biosequencefeaturefact
     where
        biosequenceob = biosequenceobid
     order by
        featurestart,
        featurestop,
        featuretype;
   
   fetch cursr into feattype, featstart, featstop, featxref, featcom, featevid;
   
   -- FEATURES
   if (speciesVal != '') or FOUND then
      seqbuff := 'FEATURES              Location/Qualifiers'||chr(10);
      strbuff := strbuff||seqbuff;
   end if;

   -- TAXON (Feature)
   if (speciesVal != '') then
      seqbuff := '     source           1..'||seqlen||chr(10);
      strbuff := strbuff||seqbuff;
      seqbuff := '                     /organism="'||speciesVal||'"'||chr(10);
      strbuff := strbuff||seqbuff;
      if (taxidVal != '') then
          seqbuff := '                     /db_xref="taxon:'||taxidVal||'"'||chr(10);
          strbuff := strbuff||seqbuff;
      end if;
   end if;

   -- CDS and GENES
   lastfeature := 'blurb';
   lastseqstart := -1;
   lastseqstop := -1;
   while FOUND loop
      if (feattype <> lastfeature or featstart <> lastseqstart or featstop <> lastseqstop) then
         if featstop >= featstart then
            seqbuff := '     '||rpad(feattype,16,' ')||featstart||'..'||featstop||chr(10);
         else
            seqbuff := '     '||rpad(feattype,16,' ')||'complement('||featstop||'..'||featstart||')'||chr(10);
         end if;
         strbuff := strbuff||seqbuff;
         lastfeature := feattype;
         lastseqstart := featstart;
         lastseqstop := featstop;
      end if;
      if (featxref != '') then
         seqbuff := '                     /db_xref="'||featxref||'"'||chr(10);
         strbuff := strbuff||seqbuff;
      end if;
      if (featevid != '') then
         seqbuff := '                     /evidence="'||featevid||'"'||chr(10);
         strbuff := strbuff||seqbuff;
      end if;
      if (featcom != '') then
         seqbuff := '                     /comment="'||featcom||'"'||chr(10);
         strbuff := strbuff||seqbuff;
      end if;
      fetch cursr into feattype, featstart, featstop, featxref, featcom, featevid;
   end loop;

   close cursr;
   
/*   -- COMMENTS formatted into lines of 68 chars plus 'COMMENT     '
   comments := getAgResearchGenbankComments(seqname,dbname);
   if (length(comments) > 0) then
      seqbuff := rpad('COMMENT',12,' ');
      strbuff := strbuff||seqbuff;
      position := 1;
      basesize := 68;
      while (position <= length(comments)) loop
         seqbuff := substr(comments,position,basesize);
         seqbuff := seqbuff || chr(10);
         strbuff := strbuff||seqbuff;
         position := position + 68;
         if (position < length(comments)) then
            seqbuff := lpad(' ',12,' ');
            strbuff := strbuff||seqbuff;
         end if;
      end loop;
   end if;*/

   -- ORIGIN
   seqbuff := 'ORIGIN      ';
   strbuff := strbuff||seqbuff;

   if (seqstr is not null) then
      -- <7-9 spaces base number> <6 groups of 10 bases>
      position := 1;
      basesize := 10;
      while (position <= seqlen) loop
         if (mod(position,60) = 1) then
            seqbuff := chr(10)||lpad(to_char(position,'FM99999999'),9,' ')||' ';
            strbuff := strbuff||seqbuff;
         end if;
         seqbuff := substr(seqstr,position,basesize);
         seqbuff := seqbuff || ' ';
         strbuff := strbuff||seqbuff;
         position := position + 10;
      end loop;
   end if;

   -- //
   seqbuff := chr(10)||'//'||chr(10);
   strbuff := strbuff||seqbuff;

   return strbuff;
END
$_$;


ALTER FUNCTION public.getgenbankrecord(character varying) OWNER TO agrbrdf;

