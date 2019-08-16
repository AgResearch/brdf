--
-- Name: getagresearchfastarecord(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getagresearchfastarecord(character varying) RETURNS text
    LANGUAGE plpgsql
    AS $_$  

DECLARE
   cursr refcursor;

   biosequenceobid integer;
   seqname varchar;
   seqbuff text;
   strbuff text;

BEGIN
   --Test if obid is an obid or is an xreflsid
   select into biosequenceobid obid from biosequenceob where xreflsid = $1;
   if not FOUND then
      biosequenceobid := $1;
   end if;
   
   strbuff := '';

   open cursr for
    select
       xreflsid ,
       seqstring
    from
       biosequenceob
    where
       obid = biosequenceobid;
    
   fetch cursr into seqname, seqbuff;

   close cursr;
   
   strbuff := '>'||seqname||chr(10)||seqbuff;
   

   return strbuff;
END
$_$;


ALTER FUNCTION public.getagresearchfastarecord(character varying) OWNER TO agrbrdf;

