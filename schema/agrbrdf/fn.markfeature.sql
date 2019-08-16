--
-- Name: markfeature(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION markfeature(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql IMMUTABLE
    AS $_$
declare
   argobid alias for $1;
   argfeaturetype alias for $2;
   markmethod alias for $3;
   markedseqstring varchar;
   featstart integer;
   featstop integer;
   featstrand integer;
   featCursor refcursor;
begin

   if markmethod != 'lowercase' and markmethod != 'X' then
      raise exception 'only lower case or X masking is currently supported';
   end if;

  
   -- examples : 7612140, 7466140
   select seqstring into markedseqstring from 
   biosequenceob where obid = argobid;

   

   open featCursor for 
   select featurestart,featurestop,featurestrand
   from biosequencefeaturefact where
   biosequenceob = argobid and featuretype = argfeaturetype;

   fetch featCursor into featstart,featstop,featstrand;

   while FOUND loop
      if featstrand <= 0  then
         raise exception 'only features on + strand are currently supported';
      end if;
 
      markedseqstring := overlay(markedseqstring placing lower(substr(markedseqstring,featstart,1+featstop-featstart)) from featstart for 1+ featstop-featstart );    

      fetch featCursor into featstart,featstop,featstrand;
   end loop;

   close featCursor;

   if markmethod = 'X' then
      markedseqstring := replace(replace(replace(replace(markedseqstring,'a','X'),'c','X'),'g','X'),'t','X');
   end if;
  
   return markedseqstring;
end;
$_$;


ALTER FUNCTION public.markfeature(integer, character varying, character varying) OWNER TO agrbrdf;

