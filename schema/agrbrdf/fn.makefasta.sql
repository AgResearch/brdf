--
-- Name: makefasta(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION makefasta(character varying, character varying) RETURNS text
    LANGUAGE plpgsql
    AS $_$  

DECLARE
   idline alias for $1;
   seqstring alias for $2;
   strbuff text;
   seqpos integer;

BEGIN   
   strbuff := '>' || idline || chr(10);

   seqpos := 1;

   while seqpos <= length(seqstring) loop
      strbuff := strbuff || substr(seqstring,seqpos,60) || chr(10);
      seqpos := seqpos + 60;
   end loop;

   return strbuff;
END
$_$;


ALTER FUNCTION public.makefasta(character varying, character varying) OWNER TO agrbrdf;

