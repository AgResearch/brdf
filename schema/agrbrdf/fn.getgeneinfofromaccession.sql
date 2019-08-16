--
-- Name: getgeneinfofromaccession(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgeneinfofromaccession(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   argseq alias for $1;
   infotype alias for $2;
   sqlstmnt text;
   rec record;
   geneid integer;
   vartemp varchar;
begin
   geneid := null;
   select getGeneidFromAccession(argseq,20) into geneid;
   
   if geneid is not null then
      sqlstmnt = 'select ' || infotype || ' as infotype from gene_info where geneid = ' || to_char(geneid,'9999999999');
      --raise notice '%',sqlstmnt;
   
      FOR rec in EXECUTE sqlstmnt LOOP 
         if upper(infotype) = 'TAX_ID' then
            return to_char(rec.infotype,'9999999');
         elsif upper(infotype) = 'DESCRIPTION' then
            vartemp := rec.infotype;
            return vartemp;
         else
            return rec.infotype;
         end if;
         exit;
      END LOOP;
   end if;

   return null;

end;$_$;


ALTER FUNCTION public.getgeneinfofromaccession(character varying, character varying) OWNER TO agrbrdf;

