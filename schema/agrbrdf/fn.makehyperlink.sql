--
-- Name: makehyperlink(character varying, character varying, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION makehyperlink(character varying, character varying, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   argurl alias for $1;
   argdisplay alias for $2;
   argurlbindvalue alias for $3;
   argtarget alias for $4;
   hyperlink varchar(5192);
BEGIN
   hyperlink := argurl;
 
   if argurlbindvalue is not null then
      hyperlink := replace(hyperlink,'$$',argurlbindvalue);
   end if;

   hyperlink := '<a href="' || hyperlink || '" ';

   if argtarget is not null then 
      hyperlink := hyperlink || ' target=' || argtarget;
   end if;

   hyperlink := hyperlink || '>' || argdisplay || '</a>';

   return hyperlink;
END;
$_$;


ALTER FUNCTION public.makehyperlink(character varying, character varying, character varying, character varying) OWNER TO agrbrdf;

